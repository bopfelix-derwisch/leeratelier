"""Atelier-portaal :8793 -- WP-06.

Het gezicht van het atelier. Rendert modules uit markdown, toont op elke pagina de
budgetmeter en de storingsbanner, en praat verder uitsluitend met de bemiddelaar op
:8794. Het kent geen modellen, geen budgetdatabase en geen conserven: dat zit allemaal
achter dat ene contract.

Server-rendered HTML met Jinja2. Eén inline script, en alleen voor het pollen van een
taakstatus -- zo staat het in `CLAUDE.md` en in `app/README.md`. Geen frontend-framework,
geen browseropslag.

Bindt op 127.0.0.1: de Cloudflare-tunnel praat lokaal.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import schema
from .render import Bemiddelaar, Sjablonen, naar_html

WORTEL = Path(__file__).resolve().parent.parent
HIER = Path(__file__).resolve().parent

SPOREN = (("basis", "Basisroute"), ("waterlab", "Spoor W - Waterlab"),
          ("leefomgeving", "Spoor L - LeefomgevingLab"))

# De zes vragen van de beheerkaart, uit spec/01-competenties.md.
KAARTVELDEN = (
    ("mis", "Wat gaat hier het eerst mis?",
     "Drie realistische faalvormen. Niet de ergste denkbare, maar de waarschijnlijkste."),
    ("signaal", "Waaraan merk ik het?",
     "Per faalvorm het signaal, zoals een gebruiker het zou beschrijven. Niet de oorzaak."),
    ("check", "Wat check ik dan?",
     "Per faalvorm een concrete handeling, uitvoerbaar zonder ontwikkelaar."),
    ("escalatie", "Wanneer is het niet meer mijn probleem?",
     "Het escalatiepunt, en aan wie."),
    ("leverancier", "Wat vraag ik mijn leverancier de eerstvolgende keer?", "Drie vragen."),
    ("oordeel", "Waar neemt het model het denken over?",
     "Een alinea. Waar vervangt het systeem een oordeel dat een mens hoort te maken?"),
)


# Sysmonitor schrijft hier wat het portaal als banner moet tonen. Het portaal leidt
# zelf al iets af uit /v1/gezondheid, maar sysmonitor ziet meer: een volgelopen schijf,
# een unit die niet draait, een machine die te heet wordt. Zie WP-08.
STORING_BESTAND = Path(os.environ.get("ATELIER_STORING",
                                      "/mnt/nvme/leeratelier/storing.json"))
# Ouder dan dit en de melding wordt genegeerd: een sysmonitor die zelf stilvalt, mag
# geen banner laten staan die niemand meer bijwerkt.
STORING_MAX_MIN = 90


def lees_storingsbanner(pad: Path = None):
    """Wat sysmonitor gemeld heeft, of niets. Nooit een fout naar de bezoeker."""
    pad = pad or STORING_BESTAND
    try:
        d = json.loads(pad.read_text(encoding="utf-8"))
        if not d.get("actief") or not d.get("tekst"):
            return None
        gezet = datetime.fromisoformat(d["gezet_op"])
        if (datetime.now(timezone.utc) - gezet).total_seconds() > STORING_MAX_MIN * 60:
            return None
        return {"niveau": d.get("niveau") or "let", "tekst": d["tekst"]}
    except (OSError, ValueError, KeyError):
        return None


class VraagIn(BaseModel):
    vraag: str


def bezoeker_van(request: Request) -> str:
    """De identiteit van de bezoeker.

    WP-07 zet Cloudflare Access ervoor; die stuurt het geverifieerde e-mailadres mee
    in `Cf-Access-Authenticated-User-Email`. Zolang dat er niet staat, valt dit terug
    op een vaste lokale naam -- bruikbaar om te bouwen en te testen, en uitdrukkelijk
    niet genoeg om dit portaal publiek te maken. Zie de waarschuwing op /facilitator.
    """
    email = request.headers.get("cf-access-authenticated-user-email")
    return email or os.environ.get("ATELIER_BEZOEKER", "lokaal@orin3")


def maak_app(bemiddelaar_basis: str = None, modules_dir: Path = None) -> FastAPI:
    basis = bemiddelaar_basis or os.environ.get("ATELIER_BEMIDDELAAR",
                                                "http://127.0.0.1:8794")
    modules_dir = Path(modules_dir or WORTEL / "content" / "modules")
    mid = Bemiddelaar(basis)
    sjablonen = Sjablonen(HIER / "templates")

    app = FastAPI(title="Leeratelier portaal", version="1.0.0")
    app.mount("/static", StaticFiles(directory=str(HIER / "static")), name="static")
    app.state.modules_dir = modules_dir

    async def omhulsel(request: Request) -> dict:
        """Wat elke pagina nodig heeft: wie kijkt, hoeveel budget, welke storing."""
        bezoeker = bezoeker_van(request)
        return {"request": request, "bezoeker": bezoeker,
                "budget": await mid.budget(bezoeker),
                "gezondheid": await mid.gezondheid(),
                "storing": lees_storingsbanner()}

    def zoek_module(module_id: str):
        map_ = modules_dir / module_id
        if not map_.is_dir():
            return None, f"Module '{module_id}' bestaat niet."
        try:
            return schema.lees(map_), None
        except schema.ModuleFout as fout:
            return None, str(fout)

    # ------------------------------------------------------------- route
    @app.get("/", response_class=HTMLResponse)
    async def route(request: Request):
        modules, _ = schema.lees_alle(modules_dir)
        zichtbaar = [m for m in modules if m.gepubliceerd]
        per_spoor = {}
        for m in zichtbaar:
            per_spoor.setdefault(m.spoor, []).append(m)
        ctx = await omhulsel(request)
        ctx.update(per_spoor=per_spoor, sporen=SPOREN, zichtbaar=zichtbaar)
        return sjablonen.html("route.html", ctx)

    # ------------------------------------------------------------ module
    @app.get("/module/{module_id}", response_class=HTMLResponse)
    async def toon_module(request: Request, module_id: str):
        module, fout = zoek_module(module_id)
        ctx = await omhulsel(request)
        if fout:
            ctx.update(kop="Deze module kan niet getoond worden", melding=fout)
            return sjablonen.html("fout.html", ctx, status_code=404)

        # Regel 1 van het modulecontract: reserveer vooraf, zodat niemand halverwege
        # zonder budget valt.
        reservering_fout = None
        if module.beurten > 0:
            code, body = await mid.reserveer(ctx["bezoeker"], module.id, module.beurten)
            if code == 429:
                reservering_fout = (
                    "Je dagbudget is op, dus voor deze module kunnen geen beurten meer "
                    "gereserveerd worden. De tekst en de proeven zonder model werken gewoon; "
                    "live antwoorden zijn na middernacht weer beschikbaar."
                    + (" Er staat wel een voorberekend antwoord klaar."
                       if body.get("conserf_beschikbaar") else ""))
            ctx["budget"] = await mid.budget(ctx["bezoeker"])

        ctx.update(module=module, inhoud_html=naar_html(module.tekst),
                   reservering_fout=reservering_fout)
        return sjablonen.html("module.html", ctx)

    @app.post("/module/{module_id}/vraag")
    async def stel_vraag(request: Request, module_id: str, v: VraagIn):
        module, fout = zoek_module(module_id)
        if fout:
            return JSONResponse(status_code=404, content={"fout": "module", "melding": fout})
        voorkeur = "show" if module.modellen == ["show"] else "auto"
        code, body = await mid.vraag(bezoeker_van(request), module_id, v.vraag, voorkeur)
        if code == 429:
            return JSONResponse(status_code=429, content={
                "fout": "budget_op",
                "melding": "Je budget voor vandaag is op. Het lichte pad blijft open; "
                           "live antwoorden zijn na middernacht weer beschikbaar."
                           + (" Voor deze module staat een voorberekend antwoord klaar."
                              if body.get("conserf_beschikbaar") else ""),
                "reset_om": body.get("reset_om")})
        if code >= 400:
            return JSONResponse(status_code=502, content={
                "fout": "bemiddelaar",
                "melding": "De leerbemiddelaar antwoordt niet. Probeer het zo nog eens."})
        return body

    @app.get("/taak/{taak_id}")
    async def haal_taak(taak_id: str):
        body = await mid.taak(taak_id)
        if body is None:
            return JSONResponse(status_code=502, content={
                "status": "mislukt",
                "antwoord": "De leerbemiddelaar antwoordt niet."})
        return body

    # ---------------------------------------------------------- opdracht
    @app.get("/opdracht/{module_id}", response_class=HTMLResponse)
    async def opdracht(request: Request, module_id: str):
        module, fout = zoek_module(module_id)
        ctx = await omhulsel(request)
        pad = (module.map / "opdracht.md") if module else None
        if fout or not pad or not pad.exists():
            ctx.update(kop="Geen opdracht",
                       melding=fout or "Bij deze module hoort geen opdracht.")
            return sjablonen.html("fout.html", ctx, status_code=404)
        ctx.update(module=module, inhoud_html=naar_html(pad.read_text(encoding="utf-8")))
        return sjablonen.html("opdracht.html", ctx)

    # ------------------------------------------------------- beheerkaart
    @app.get("/beheerkaart", response_class=HTMLResponse)
    async def beheerkaart(request: Request):
        ctx = await omhulsel(request)
        ctx.update(velden=KAARTVELDEN)
        return sjablonen.html("beheerkaart.html", ctx)

    @app.post("/beheerkaart/export")
    async def beheerkaart_export(
        toepassing: str = Form(...), ingevuld_door: str = Form(""),
        organisatie: str = Form(""), mis: str = Form(""), signaal: str = Form(""),
        check: str = Form(""), escalatie: str = Form(""), leverancier: str = Form(""),
        oordeel: str = Form(""),
    ):
        waarden = {"mis": mis, "signaal": signaal, "check": check,
                   "escalatie": escalatie, "leverancier": leverancier, "oordeel": oordeel}
        regels = [f"# Beheerkaart - {toepassing}", "",
                  f"Ingevuld door: {ingevuld_door} &middot; Organisatie: {organisatie}", ""]
        for i, (veld, kop, hulp) in enumerate(KAARTVELDEN, 1):
            regels += [f"## {i}. {kop}", hulp, "", (waarden[veld] or "").strip(), ""]
        regels += ["---", "",
                   "Ingevuld in het Leeratelier op orin3. Indicatief, geen operationeel advies."]
        naam = "".join(c if c.isalnum() or c in "-_" else "-" for c in toepassing.lower())[:60]
        return PlainTextResponse(
            "\n".join(regels), media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="beheerkaart-{naam}.md"'})

    # ------------------------------------------------------- vastgelopen
    @app.post("/vastgelopen", response_class=HTMLResponse)
    async def vastgelopen(request: Request, tekst: str = Form(...),
                          module_id: str = Form(""), laatste_vraag: str = Form(""),
                          laatste_bron: str = Form("")):
        bezoeker = bezoeker_van(request)
        stand = await mid.budget(bezoeker)
        gez = await mid.gezondheid()
        # Contextvangst: dit is wat een melding bruikbaar maakt zonder heen-en-weer.
        context = {"laatste_vraag": laatste_vraag or None,
                   "bron": laatste_bron or None,
                   "budget_resterend": stand.get("persoonlijk_resterend"),
                   "klasmodel": gez.get("klasmodel"),
                   "showmodel": gez.get("showmodel"),
                   "index_leeftijd_dagen": gez.get("rag_index_leeftijd_dagen"),
                   "storingsmodus": gez.get("storingsmodus")}
        _, body = await mid.melding(bezoeker, module_id, tekst, context)
        ctx = await omhulsel(request)
        ctx.update(module_id=module_id,
                   reactietermijn=body.get("reactietermijn",
                                           "Je melding is opgeslagen."))
        return sjablonen.html("melding_ok.html", ctx)

    # ------------------------------------------------------- facilitator
    @app.get("/facilitator", response_class=HTMLResponse)
    async def facilitator(request: Request):
        modules, fouten = schema.lees_alle(modules_dir)
        ctx = await omhulsel(request)
        ctx.update(modules=modules, fouten=fouten)
        return sjablonen.html("facilitator.html", ctx)

    # -------------------------------------------------------- gezondheid
    @app.get("/gezondheid")
    async def gezondheid(request: Request):
        modules, fouten = schema.lees_alle(modules_dir)
        keten = await mid.gezondheid()
        storing = lees_storingsbanner()
        return {"portaal": "actief",
                "storingsbanner": storing["tekst"] if storing else None,
                "bemiddelaar": "weg" if keten.get("bemiddelaar") == "weg" else "actief",
                "modules_totaal": len(modules),
                "modules_gepubliceerd": sum(1 for m in modules if m.gepubliceerd),
                "modules_stuk": len(fouten), "fouten": fouten,
                "keten": keten}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/favicon.ico")
    async def favicon():
        return RedirectResponse("/static/atelier.css", status_code=204)

    return app


# Uvicorn start hem als fabriek, net als de bemiddelaar:
#   python3 -m uvicorn app.main:maak_app --factory --host 127.0.0.1 --port 8793
