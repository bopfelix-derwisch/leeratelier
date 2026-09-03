"""Wachtrij en degradatieladder.

De harde eis uit het contract: **wachten is acceptabel, stilte niet.** Elke vraag
krijgt binnen twee seconden een positie en een schatting terug, ook als het antwoord
zelf een minuut duurt. `POST /v1/vraag` blokkeert daarom nooit; hij zet een taak in
de rij en geeft meteen een taak-id.

Eén rij per model, met zoveel gelijktijdige werkers als `config/budget.yaml` toestaat
(gemeten in WP-01 en WP-04: 4 voor het klasmodel, 2 voor het showmodel). Meer werkers
kopen geen doorzet maar wachttijd -- de machine zit al bij één gebruiker op 93 procent
GPU.

FIFO, geen prioriteiten: het atelier heeft één soort bezoeker.
"""

from __future__ import annotations

import asyncio
import statistics
import time
import uuid
from dataclasses import dataclass, field

from . import modellen
from .modellen import ModelWeg

WACHTEND, BEZIG, KLAAR, MISLUKT = "wachtend", "bezig", "klaar", "mislukt"


@dataclass
class Taak:
    taak_id: str
    bezoeker_id: str
    module_id: str
    vraag: str
    model: str                      # "klas" of "show"
    status: str = WACHTEND
    antwoord: str = ""
    bron: str = ""                  # cache | klas | show | conserf
    latency_ms: int = 0
    beurten_verbruikt: int = 0
    fout: str = ""
    aangemaakt: float = field(default_factory=time.monotonic)


class Wachtrij:
    """Houdt per model een rij en een aantal werkers.

    De werkers worden bij het starten van de app aangemaakt en bij het stoppen
    netjes afgebroken. `verwerk` is meegegeven in plaats van hier ingebakken, zodat
    de ladder in `main.py` staat waar hij te lezen is en deze klasse alleen over
    wachten gaat.
    """

    def __init__(self, inst, verwerk):
        self.inst = inst
        self.verwerk = verwerk
        self.taken: dict = {}
        self.rijen = {m: asyncio.Queue() for m in ("klas", "show")}
        self._werkers: list = []
        # Rollende meting van de echte duur per model, voor de schatting.
        # Beginwaarden komen uit ops/ijking/, niet uit de duim.
        self._duren = {m: [inst.mediaan_s[m]] for m in ("klas", "show")}

    # -- levenscyclus -------------------------------------------------------
    async def start(self) -> None:
        for model, aantal in self.inst.gelijktijdig.items():
            for i in range(max(1, int(aantal))):
                self._werkers.append(asyncio.create_task(
                    self._werker(model), name=f"werker-{model}-{i}"))

    async def stop(self) -> None:
        for w in self._werkers:
            w.cancel()
        for w in self._werkers:
            try:
                await w
            except (asyncio.CancelledError, Exception):
                pass
        self._werkers = []

    # -- inzicht ------------------------------------------------------------
    def diepte(self, model: str = None) -> int:
        if model:
            return self.rijen[model].qsize()
        return sum(q.qsize() for q in self.rijen.values())

    def mediaan_s(self, model: str) -> float:
        return statistics.median(self._duren[model])

    def positie(self, taak_id: str) -> int:
        """Hoeveel taken staan er vóór deze in de rij? Nul betekent: aan de beurt."""
        taak = self.taken.get(taak_id)
        if not taak or taak.status != WACHTEND:
            return 0
        wachtend = [t for t in self.taken.values()
                    if t.status == WACHTEND and t.model == taak.model]
        wachtend.sort(key=lambda t: t.aangemaakt)
        for i, t in enumerate(wachtend):
            if t.taak_id == taak_id:
                return i
        return 0

    def schat_wachten_s(self, model: str, positie: int) -> int:
        """Positie maal de gemeten mediaan, gedeeld door het aantal werkers."""
        werkers = max(1, int(self.inst.gelijktijdig.get(model, 1)))
        return int((positie + 1) * self.mediaan_s(model) / werkers)

    # -- gebruik ------------------------------------------------------------
    def dien_in(self, bezoeker_id: str, module_id: str, vraag: str, model: str) -> Taak:
        taak = Taak(taak_id=uuid.uuid4().hex, bezoeker_id=bezoeker_id,
                    module_id=module_id, vraag=vraag, model=model)
        self.taken[taak.taak_id] = taak
        self.rijen[model].put_nowait(taak)
        return taak

    def voeg_klaar_toe(self, taak: Taak) -> Taak:
        """Registreer een taak die de rij niet in hoeft: cache- of conserf-treffer.

        Die krijgen ook een taak-id, zodat het portaal maar één manier van ophalen
        kent en de bezoeker geen verschil merkt in de afhandeling -- alleen in het
        bronlabel, en dat is met opzet zichtbaar.
        """
        taak.status = KLAAR
        self.taken[taak.taak_id] = taak
        return taak

    # -- werker -------------------------------------------------------------
    async def _werker(self, model: str) -> None:
        rij = self.rijen[model]
        while True:
            taak = await rij.get()
            taak.status = BEZIG
            start = time.monotonic()
            try:
                await self.verwerk(taak)
            except asyncio.CancelledError:
                taak.status = MISLUKT
                taak.fout = "afgebroken"
                raise
            except Exception as fout:                       # noqa: BLE001
                taak.status = MISLUKT
                taak.fout = str(fout)[:200]
            finally:
                rij.task_done()
            if taak.status == KLAAR and taak.bron in ("klas", "show"):
                duur = time.monotonic() - start
                self._duren[model].append(duur)
                del self._duren[model][:-20]        # alleen de laatste twintig


async def vraag_met_terugval(inst, model: str, tekst: str):
    """Vraag het gekozen model; valt terug op het andere als dat wegvalt.

    Trede 2 en 3 van de ladder. Een bezoeker die het klasmodel vraagt terwijl dat
    net omvalt, hoort niet te merken dat er iets aan de hand is behalve dat het
    antwoord trager komt en anders gelabeld is.
    """
    volgorde = [model] + [m for m in ("klas", "show") if m != model]
    laatste = None
    for kandidaat in volgorde:
        endpoint = inst.modellen[kandidaat]["endpoint"]
        try:
            antwoord, latency_ms = await modellen.vraag(endpoint, tekst)
            return antwoord, latency_ms, kandidaat
        except ModelWeg as fout:
            laatste = fout
    raise ModelWeg(str(laatste) if laatste else "geen model bereikbaar")
