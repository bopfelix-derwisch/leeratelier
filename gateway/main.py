"""Leerbemiddelaar :8794 -- WP-05.

Het enige echt nieuwe stuk techniek in dit atelier. Hij bestaat omdat één 32B-model
breekt zodra er meer dan één bezoeker tegelijk iets vraagt, en omdat het atelier
permanent en onbewaakt open staat.

De degradatieladder staat in `_ladder_bij_indienen` en `verwerk`, met opzet bij elkaar
en in leesvolgorde:

    1 cache      identieke genormaliseerde vraag binnen de bewaartermijn
    2 klas       standaard; klasmodel op :8081
    3 show       als de module erom vraagt of het klasmodel weg is
    4 conserf    budget op, wachtrij vol, of geen enkel model bereikbaar
    5 licht pad  melding dat live antwoorden na middernacht terugkomen

Niemand krijgt "nee". De gekozen trede gaat altijd mee in het antwoord, want de
bezoeker moet kunnen zien waar zijn antwoord vandaan komt -- dat is zelf lesmateriaal.

Bindt op 127.0.0.1: de Cloudflare-tunnel praat lokaal, en deze dienst is niet
publiek bereikbaar. Alleen het portaal praat ermee.
"""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import instellingen as inst_mod
from . import modellen
from .budget import Budget, BudgetOp
from .cache import Cache
from .conserven import Conserven
from .db import verbind
from .logboek import Logboek
from .wachtrij import KLAAR, MISLUKT, WACHTEND, Taak, Wachtrij, vraag_met_terugval
from .modellen import ModelWeg

# Boven deze rijdiepte krijgt een nieuwe vraag meteen een conserf in plaats van
# een plek in de rij. Crit-drempel uit plan par. 8.
RIJ_CRIT = 8


class VraagIn(BaseModel):
    bezoeker_id: str
    module_id: str
    vraag: str
    model_voorkeur: str = Field(default="auto", pattern="^(auto|klas|show)$")


class ReserveerIn(BaseModel):
    bezoeker_id: str
    module_id: str
    beurten: int = 1


class MeldingIn(BaseModel):
    bezoeker_id: str
    module_id: str = ""
    tekst: str
    context: dict = Field(default_factory=dict)


def rag_leeftijd_dagen(rag_dir: Path):
    pad = Path(rag_dir) / "vectors.npy"
    if not pad.exists():
        return None
    gebouwd = datetime.fromtimestamp(pad.stat().st_mtime, tz=timezone.utc)
    return (datetime.now(timezone.utc) - gebouwd).days


def maak_app(inst=None) -> FastAPI:
    inst = inst or inst_mod.laad()
    con = verbind(inst.db_pad)
    budget = Budget(con, inst)
    cache = Cache(con, inst)
    logboek = Logboek(con, inst)
    conserven = Conserven(inst.conserven_dir)

    async def verwerk(taak: Taak) -> None:
        """Trede 2, 3 en 4: model, ander model, conserf."""
        try:
            antwoord, latency_ms, gebruikt = await vraag_met_terugval(
                inst, taak.model, taak.vraag)
            taak.antwoord, taak.latency_ms, taak.bron = antwoord, latency_ms, gebruikt
            taak.model = gebruikt
            taak.beurten_verbruikt = 1
            # Eerst afboeken en cachen, dan pas op klaar zetten. Andersom ziet een
            # bezoeker die meteen doorvraagt een stand die nog niet bijgewerkt is:
            # de cache mist, of het budget laat een beurt door die al vergeven was.
            await asyncio.to_thread(budget.boek_af, taak.bezoeker_id, 1)
            await asyncio.to_thread(cache.bewaar, taak.vraag, taak.module_id,
                                    gebruikt, antwoord)
            taak.status = KLAAR
        except ModelWeg as fout:
            conserf = (conserven.zoek(taak.module_id, taak.vraag)
                       or conserven.eerste(taak.module_id))
            # De reservering gaat terug: een conserf kost geen modelbeurt, en de
            # bezoeker mag niet betalen voor een storing die hij niet veroorzaakte.
            await asyncio.to_thread(budget.geef_terug, taak.bezoeker_id, 1)
            if conserf:
                taak.antwoord, taak.bron = conserf.antwoord, "conserf"
                taak.beurten_verbruikt = 0
                taak.status = KLAAR
            else:
                taak.status, taak.fout = MISLUKT, str(fout)[:200]
                taak.antwoord = (
                    "Er draait op dit moment geen taalmodel en voor deze module staat "
                    "geen voorberekend antwoord klaar. De pagina's en dashboards werken "
                    "gewoon door; live antwoorden zijn na middernacht weer beschikbaar.")
        finally:
            # De modelnaam, niet de laddertrede: die staat al in `bron`. Het logboek
            # is het materiaal voor module K6, en "Qwen3-8B" zegt daar meer dan "klas".
            naam = inst.modellen.get(taak.model, {}).get("naam", taak.model)
            await asyncio.to_thread(
                logboek.schrijf, taak.bezoeker_id, taak.module_id, taak.vraag,
                naam, taak.bron or "geen", taak.latency_ms,
                taak.beurten_verbruikt, taak.status == KLAAR)

    rij = Wachtrij(inst, verwerk)

    async def dagelijks_opruimen() -> None:
        """Logboek en cache opruimen. Draait elke zes uur, niet op een kloktijd.

        Een taak die op middernacht wacht, mist zijn slag als de dienst net dan
        herstart. Elke zes uur is vaker dan nodig en ongevoelig voor herstarts.
        """
        while True:
            try:
                await asyncio.to_thread(logboek.ruim_op)
                await asyncio.to_thread(cache.ruim_op)
            except Exception:                                  # noqa: BLE001
                pass
            await asyncio.sleep(6 * 3600)

    @asynccontextmanager
    async def levensduur(_app: FastAPI):
        await rij.start()
        opruimer = asyncio.create_task(dagelijks_opruimen(), name="opruimer")
        try:
            yield
        finally:
            opruimer.cancel()
            await rij.stop()
            con.close()

    app = FastAPI(title="Leeratelier bemiddelaar", version="1.0.0", lifespan=levensduur)
    app.state.inst = inst
    app.state.rij = rij
    app.state.conserven = conserven

    # ---------------------------------------------------------------- vraag
    @app.post("/v1/vraag", status_code=202)
    async def stel_vraag(v: VraagIn):
        model = "klas" if v.model_voorkeur == "auto" else v.model_voorkeur

        # Trede 1: cache. Kost geen beurt en gaat de rij niet in.
        gecachet = await asyncio.to_thread(cache.zoek, v.vraag, v.module_id, model)
        if gecachet:
            taak = rij.voeg_klaar_toe(Taak(
                taak_id=os.urandom(16).hex(), bezoeker_id=v.bezoeker_id,
                module_id=v.module_id, vraag=v.vraag, model=model,
                antwoord=gecachet, bron="cache"))
            await asyncio.to_thread(
                logboek.schrijf, v.bezoeker_id, v.module_id, v.vraag,
                inst.modellen.get(model, {}).get("naam", model), "cache", 0, 0, True)
            return {"taak_id": taak.taak_id, "positie": 0, "geschat_wachten_s": 0,
                    "verwachte_bron": "cache", "beurten_gereserveerd": 0}

        # Budget. Bij uitputting geen weigering maar een verwijzing naar het conserf.
        try:
            await asyncio.to_thread(budget.controleer, v.bezoeker_id)
        except BudgetOp as op:
            return JSONResponse(status_code=429, content={
                "fout": "budget_op", "welk": op.welk, "reset_om": op.reset_om,
                "conserf_beschikbaar": conserven.heeft(v.module_id)})

        # Trede 4 vooraf: rij te diep, dan meteen een conserf in plaats van wachten.
        if rij.diepte(model) >= RIJ_CRIT:
            conserf = conserven.zoek(v.module_id, v.vraag) or conserven.eerste(v.module_id)
            if conserf:
                taak = rij.voeg_klaar_toe(Taak(
                    taak_id=os.urandom(16).hex(), bezoeker_id=v.bezoeker_id,
                    module_id=v.module_id, vraag=v.vraag, model=model,
                    antwoord=conserf.antwoord, bron="conserf"))
                return {"taak_id": taak.taak_id, "positie": 0, "geschat_wachten_s": 0,
                        "verwachte_bron": "conserf", "beurten_gereserveerd": 0}

        # Reserveer één beurt, tenzij het portaal er al een voor deze module opzij zette.
        gereserveerd = 0
        if await asyncio.to_thread(budget.reservering, v.bezoeker_id) == 0:
            gereserveerd = await asyncio.to_thread(budget.reserveer, v.bezoeker_id, 1)

        taak = rij.dien_in(v.bezoeker_id, v.module_id, v.vraag, model)
        positie = rij.positie(taak.taak_id)
        return {"taak_id": taak.taak_id, "positie": positie,
                "geschat_wachten_s": rij.schat_wachten_s(model, positie),
                "verwachte_bron": model, "beurten_gereserveerd": gereserveerd or 1}

    # ----------------------------------------------------------------- taak
    @app.get("/v1/taak/{taak_id}")
    async def haal_taak(taak_id: str):
        taak = rij.taken.get(taak_id)
        if not taak:
            return JSONResponse(status_code=404, content={"fout": "taak_onbekend"})
        return {
            "status": taak.status,
            "positie": rij.positie(taak_id) if taak.status == WACHTEND else None,
            "antwoord": taak.antwoord or None,
            "bron": taak.bron or None,
            "model": inst.modellen.get(taak.model, {}).get("naam") if taak.bron in ("klas", "show") else None,
            "latency_ms": taak.latency_ms or None,
            "beurten_verbruikt": taak.beurten_verbruikt,
            # Gaat expliciet mee bij elk antwoord. Module K4 leert bezoekers hiernaar
            # te vragen; het zou raar zijn als het atelier het zelf verzweeg.
            "index_leeftijd_dagen": rag_leeftijd_dagen(inst.rag_dir),
            "fout": taak.fout or None,
        }

    # --------------------------------------------------------------- budget
    @app.get("/v1/budget/{bezoeker_id}")
    async def haal_budget(bezoeker_id: str):
        s = await asyncio.to_thread(budget.stand, bezoeker_id)
        return {"persoonlijk_resterend": s.persoonlijk_resterend,
                "persoonlijk_totaal": s.persoonlijk_totaal,
                "dag_resterend": s.dag_resterend, "dag_totaal": s.dag_totaal,
                "reset_om": s.reset_om}

    @app.post("/v1/reserveer")
    async def reserveer(r: ReserveerIn):
        try:
            n = await asyncio.to_thread(budget.reserveer_minstens, r.bezoeker_id, r.beurten)
        except BudgetOp as op:
            return JSONResponse(status_code=429, content={
                "fout": "budget_op", "welk": op.welk, "reset_om": op.reset_om,
                "conserf_beschikbaar": conserven.heeft(r.module_id)})
        return {"ok": True, "gereserveerd": n, "vervalt_om": budget.reset_om()}

    # ----------------------------------------------------------- gezondheid
    @app.get("/v1/gezondheid")
    async def gezondheid():
        klas, show, embed = await asyncio.gather(
            modellen.leeft(inst.modellen["klas"]["endpoint"]),
            modellen.leeft(inst.modellen["show"]["endpoint"]),
            modellen.leeft(inst.modellen["embed"]["endpoint"]))
        pct = await asyncio.to_thread(budget.dag_verbruikt_pct)
        open_meld = await asyncio.to_thread(logboek.open_meldingen)
        return {
            "klasmodel": "actief" if klas else "weg",
            "showmodel": "actief" if show else "weg",
            "embeddings": "actief" if embed else "weg",
            "wachtrij_diepte": rij.diepte(),
            "dagbudget_verbruikt_pct": pct,
            "rag_index_leeftijd_dagen": rag_leeftijd_dagen(inst.rag_dir),
            # Storingsmodus zodra er geen enkel model meer is: het portaal zet
            # daarop zijn banner. Conserven houden de route dan overeind.
            "storingsmodus": not (klas or show),
            "open_meldingen": open_meld,
            "conserven": conserven.aantal,
            "p95_latency_ms": await asyncio.to_thread(logboek.p95_latency_ms),
        }

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # ------------------------------------------------------------- melding
    @app.post("/v1/melding")
    async def melding(m: MeldingIn):
        mid = await asyncio.to_thread(logboek.melding, m.bezoeker_id, m.module_id,
                                      m.tekst, m.context)
        return {"ok": True, "melding_id": mid,
                "reactietermijn": "Dit is een prive-lab van een persoon. "
                                  "Storingen kunnen dagen duren."}

    return app


# Geen module-level app: `maak_app` opent een databaseverbinding en zou dat bij elke
# import doen, ook in een test. Uvicorn start hem als fabriek:
#   python3 -m uvicorn gateway.main:maak_app --factory --host 127.0.0.1 --port 8794
