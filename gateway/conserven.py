"""Conserven: voorberekende antwoorden, trede 4 van de degradatieladder.

Twee functies, en de tweede is de belangrijkste. Ze vlakken de piek af doordat
iedereen ongeveer dezelfde demovragen stelt, en ze houden de hele route beschikbaar
terwijl er geen model draait. Het atelier staat permanent en onbewaakt open; zonder
conserven is een weggevallen model gelijk aan een gesloten atelier.

Een conserf is dus geen noodrem maar een volwaardig pad -- en het portaal labelt het
altijd zichtbaar als voorberekend. Een atelier dat leert antwoorden te wantrouwen,
mag zelf niet verzwijgen waar een antwoord vandaan komt.

Formaat per module, `content/conserven/k04.json`:

    {"module_id": "...", "gegenereerd_op": "...", "model": "...",
     "antwoorden": [{"vraag_genormaliseerd": "...", "antwoord": "...",
                     "bron_labels": ["..."]}]}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .cache import normaliseer


@dataclass
class Conserf:
    antwoord: str
    model: str
    gegenereerd_op: str
    bron_labels: list


class Conserven:
    """Leest de conserven van schijf en houdt ze in geheugen.

    Herladen kan met `herlaad()`; het portaal hoeft daar niet voor te herstarten.
    Ontbrekende of kapotte bestanden zijn geen fout: dan is er simpelweg geen
    conserf voor die module, en de ladder valt een trede verder. Nette degradatie
    boven harde aannames.
    """

    def __init__(self, map_: Path):
        self.map = Path(map_)
        self._per_module: dict = {}
        self.herlaad()

    def herlaad(self) -> int:
        self._per_module = {}
        if not self.map.is_dir():
            return 0
        for pad in sorted(self.map.glob("*.json")):
            try:
                data = json.loads(pad.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            module_id = data.get("module_id") or pad.stem
            per_vraag = {}
            for a in data.get("antwoorden") or []:
                sleutel = a.get("vraag_genormaliseerd")
                if not sleutel or not a.get("antwoord"):
                    continue
                per_vraag[normaliseer(sleutel)] = Conserf(
                    antwoord=a["antwoord"],
                    model=data.get("model", "onbekend"),
                    gegenereerd_op=data.get("gegenereerd_op", ""),
                    bron_labels=a.get("bron_labels") or [],
                )
            if per_vraag:
                self._per_module[module_id] = per_vraag
        return sum(len(v) for v in self._per_module.values())

    def zoek(self, module_id: str, vraag: str):
        """Exacte treffer op de genormaliseerde vraag, anders niets.

        Bewust geen semantische match: een conserf dat 'ongeveer' past, is precies
        het soort stille aanname dat module K4 leert wantrouwen.
        """
        return (self._per_module.get(module_id) or {}).get(normaliseer(vraag))

    def eerste(self, module_id: str):
        """Willekeurig conserf van een module, als uitwijk bij storing.

        Beter een voorberekend antwoord op een naburige vraag, zichtbaar gelabeld,
        dan een leeg scherm -- mits het portaal erbij zet dat dit niet het antwoord
        op de gestelde vraag is.
        """
        per_vraag = self._per_module.get(module_id) or {}
        for conserf in per_vraag.values():
            return conserf
        return None

    def heeft(self, module_id: str) -> bool:
        return bool(self._per_module.get(module_id))

    @property
    def aantal(self) -> int:
        return sum(len(v) for v in self._per_module.values())
