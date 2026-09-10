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
          ("leefomgeving", "Spoor L - LeefomgevingLab"),
          ("sturing", "Route Sturing"))

# Twee routes voor twee doelgroepen. Ze delen de machine, de POC's en de principes,
# maar niet het eindproduct: wie beheert wil weten wat er stukgaat, wie beslist wil
# weten wat hij tekent. Het keuzemenu staat op /start (besluit B34).
ROUTES = (
    {"id": "beheer", "naam": "Beheer en techniek",
     "voor": "functioneel beheerders, product owners en technisch geinteresseerden",
     "zin": "Je werkt met een AI-toepassing, of gaat dat doen, en wilt weten wat er "
            "onder de motorkap gebeurt en wanneer een antwoord niet deugt. Met de "
            "businesswaarde erbij: wat het oplevert, en waarom opschalen het lastige "
            "deel is.",
     "sporen": ("basis", "waterlab", "leefomgeving"),
     "kaart_url": "/beheerkaart", "kaart_naam": "beheerkaart",
     "kaart_zin": "een A4 over je eigen toepassing: wat gaat er mis, en wat check je dan"},
    {"id": "sturing", "naam": "Sturing en besluit",
     "voor": "informatiemanagers, programmamanagers en algemeen managers",
     "zin": "Je beslist over AI-toepassingen zonder ze zelf te bouwen of te beheren, "
            "en wilt weten wat je koopt, wat het later kost en waar je voor tekent. "
            "Met een werkende case in het midden: de IJssel-verwachting van Waterlab, "
            "waarin lokale AI, open source, een cloudmodel en een agentische stap "
            "samenkomen op een apparaat van tweeduizend euro.",
     "sporen": ("sturing",),
     "kaart_url": "/besluitkaart", "kaart_naam": "besluitkaart",
     "kaart_zin": "een A4 over het besluit dat voorligt: wat is beloofd, wie merkt het "
                  "eerst als het misgaat, en waaraan zie je dat je moet stoppen"},
)


# De zes vragen van de besluitkaart. Spiegelbeeld van KAARTVELDEN: dezelfde opzet,
# maar gesteld vanuit degene die tekent in plaats van degene die het draaiend houdt.
BESLUITVELDEN = (
    ("besluit", "Welk besluit ligt er werkelijk voor?",
     "Bouwen, kopen, doorgaan of stoppen. Schrijf het op als een keuze, niet als een wens."),
    ("belofte", "Wat wordt er beloofd, en wie kan dat controleren?",
     "De belofte in de woorden van de leverancier of de bouwer. Daarachter: wie kan "
     "onafhankelijk vaststellen of het waar is, en heeft die persoon dat gedaan?"),
    ("mis", "Wat gaat er het eerst mis, en wie merkt dat als eerste?",
     "Niet de ergste denkbare storing, maar de waarschijnlijkste. En de naam van de "
     "functie die het als eerste voor de kiezen krijgt -- meestal niet de uwe."),
    ("rekening", "Wat kost dit als het eenmaal draait?",
     "Niet de aanschaf. Het onderhoud: wie verwerkt bronwijzigingen, wie ververst de "
     "index, wie kijkt of het nog klopt, en hoeveel van hun tijd is dat per maand?"),
    ("eigenaar", "Wie is eigenaar als het misgaat?",
     "Een naam of een rol, geen afdeling. En wat er gebeurt als die persoon vertrekt."),
    ("stoppen", "Waaraan zou je zien dat je hiermee moet stoppen?",
     "Een alinea. Formuleer dit voordat je begint; achteraf is het bijna niet meer te doen."),
)

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
# Wie de facilitatorpagina mag zien. Die toont concepten en contractfouten, en dat
# is niets voor een bezoeker. Leeg betekent: alleen wie niet achter Access zit, dus
# lokaal bouwen blijft werken en een ingelogde vreemde komt er niet in. Zie B39.
FACILITATORS = frozenset(
    e.strip().lower() for e in os.environ.get("ATELIER_FACILITATORS", "").split(",")
    if e.strip())

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


# Het verhaal op de landingspagina, in de volgorde waarin het gebeurde. De maanden
# komen uit de git-historie van de repo's, niet uit het geheugen: Derwisch begon op
# 27 februari, LeefomgevingLab op 13 mei, dit atelier op 2 september.
#
# `rijpheid` is met opzet zichtbaar. Niet alles is even af, en dat door elkaar laten
# lopen zou het verhaal platslaan tot een productcatalogus.
ACTEN = (
    {"maand": "februari", "fase": "uit nieuwsgierigheid",
     "naam": "Derwisch", "onder": "Kan techniek je ook vertragen?",
     "tekst": "Het begon klein en persoonlijk: inspreken, en iets terugkrijgen dat je "
              "aan het denken zet. Geen assistent die sneller werkt, maar een spiegel "
              "die je even stil laat staan. Draaide eerst op een klein apparaat, met "
              "een model dat ergens anders stond.",
     "keer": "Wat hier bleek: het interessante zat niet in het antwoord maar in de vraag "
             "die het model terugstelde.",
     "merken": ("spraak naar tekst", "ePaper-kiosk", "ritueel"),
     "cijfers": (("promptlagen", "3"), ("eerste commit", "27 feb")),
     "rijpheid": "draait", "viz": "puls",
     "link": "https://felixisfelix.com/", "linktekst": "Het bredere werk"},

    {"maand": "april", "fase": "de stap naar het werk",
     "naam": "Morele Helper", "onder": "Dezelfde vraag, nu voor een ambtenaar",
     "tekst": "Hetzelfde idee, maar nuchter en beroepsmatig. Eenentwintig werkdagen, elke "
              "dag kort inspreken over één beleidsdilemma. Twee vragen terug: een "
              "spiegelvraag en een vraag uit een ethisch reflectiepad. Op dag "
              "eenentwintig een leerverslag.",
     "keer": "Hier werd het persoonlijke experiment een instrument: met een ritme, een "
             "eindproduct en een beroepsgroep in gedachten.",
     "merken": ("lokale AI", "beroepsethiek", "21 werkdagen"),
     "cijfers": (("werkdagen", "21"), ("vragen per dag", "2")),
     "rijpheid": "draait, publiek nog stuk", "viz": "ritme", "link": "", "linktekst": ""},

    {"maand": "mei", "fase": "werk, met echte data",
     "naam": "LeefomgevingLab", "onder": "Leefomgeving als deelbare geo-informatie",
     "tekst": "Van reflectie naar publieke data. Geluid, lucht, externe veiligheid en "
              "afval als herbruikbaar informatieproduct — met open standaarden en een "
              "kwaliteitspagina die per bron opschrijft wat er niet aan klopt.",
     "keer": "De grootste ontdekking staat op die kwaliteitspagina: coördinaatstelsels "
             "zijn keer op keer de valkuil, en gegokte endpoints kloppen zelden.",
     "merken": ("PDOK", "WFS", "GeoParquet", "RAG"),
     "cijfers": (("commits", "243"), ("fragmenten in de index", "924")),
     "rijpheid": "volwassen", "viz": "raster",
     "link": "https://leefomgevinglab.felixisfelix.com/kwaliteit",
     "linktekst": "Kwaliteit per POC"},

    {"maand": "mei", "fase": "en toen echt zwaar",
     "naam": "Waterlab IJssel", "onder": "Een rivier, nagerekend en vooruitgekeken",
     "tekst": "Een volwaardig hydrologisch model op dezelfde machine. Het hoogwater van "
              "1995 en 2021 nagespeeld, plus een verwachting van veertien dagen op live "
              "metingen van Rijkswaterstaat en neerslag van Open-Meteo.",
     "keer": "Dit was het bewijs dat één machine in een woonkamer een echte modelketen "
             "aankan — én waar de grenzen daarvan liggen.",
     "merken": ("Wflow SBM", "Julia", "RWS Waterinfo", "deck.gl"),
     "cijfers": (("commits", "160"), ("dagen vooruit", "14")),
     "rijpheid": "volwassen", "viz": "hydro",
     "link": "https://waterlab.felixisfelix.com/", "linktekst": "Naar het dashboard"},

    {"maand": "juli", "fase": "toen het er te veel werden",
     "naam": "Labs-MCP", "onder": "Een sleutelbos voor twaalf proefopstellingen",
     "tekst": "Twaalf opstellingen betekent twaalf sets sleutels, en die stonden overal "
              "en nergens. Dus kwam er een versleutelde kluis met een programma dat ze "
              "naar de juiste plek schrijft, en een dun laagje waardoor een AI-assistent "
              "dezelfde vijf handelingen mag doen. Twee projecten zijn aangesloten, tien "
              "nog niet.",
     "keer": "Hier verschoof de vraag van bouwen naar beheersbaar houden: een "
             "proefopstelling maak je op een middag, twaalf ervan onderhouden is een "
             "apart project.",
     "merken": ("MCP", "age-kluis", "stdlib-only kern", "2 van de 12"),
     "cijfers": (("kern", "284 regels"), ("MCP-schil", "71 regels")),
     "rijpheid": "eerste stap", "viz": "sleutels",
     "link": "/module/k07-de-sleutelbos", "linktekst": "De module met het open-source-dilemma"},

    {"maand": "september", "fase": "want het moest blijven draaien",
     "naam": "Sysmonitor", "onder": "Dertien dingen tegelijk, en niemand die kijkt",
     "tekst": "Op een gegeven moment draaien er zoveel dingen tegelijk dat je niet meer "
              "weet wat er stuk is. Deze dienst bewaakt schijf, geheugen, temperatuur en "
              "twintig andere diensten — en geeft bij elke waarschuwing een commando dat "
              "je echt kunt uitvoeren.",
     "keer": "Niet bedacht maar ontstaan: uit de ervaring dat een systeem dat stilstaat "
             "er precies hetzelfde uitziet als een systeem dat werkt.",
     "merken": ("systemd", "drempels met actie", "90 dagen historie"),
     "cijfers": (("bewaakte diensten", "20"), ("drempels", "6")),
     "rijpheid": "nieuw", "viz": "hartslag",
     "link": "https://status.felixisfelix.com/", "linktekst": "Bekijk de status"},

    {"maand": "september", "fase": "en dit is de laag eroverheen",
     "naam": "Het Leeratelier", "onder": "Waar je nu bent",
     "tekst": "Alle bovenstaande projecten hebben één ding gemeen: er is meer van geleerd "
              "dan er in een eindrapport past. Dit atelier maakt dat bruikbaar voor "
              "iemand anders — vijftien modules over wat er misging en waaraan je het "
              "had kunnen zien.",
     "keer": "Het bouwt niets nieuws. Het maakt zichtbaar wat er al stond, inclusief de "
             "fouten die niemand had opgeschreven.",
     "merken": ("FastAPI", "sqlite", "geen framework", "Nederlands"),
     "cijfers": (("modules", "15"), ("voorberekende antwoorden", "33")),
     "rijpheid": "in aanbouw", "viz": "lagen",
     "link": "/route", "linktekst": "Begin de route"},
)


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


def mag_facilitator(request: Request) -> bool:
    """Mag deze bezoeker de facilitatorpagina zien?

    Twee wegen erheen. Zonder Access-header zit je lokaal op de machine -- het
    portaal luistert alleen op 127.0.0.1 en de tunnel gaat altijd langs Access, dus
    dat is de bouwsituatie. Kom je wel via Access binnen, dan moet je adres in
    `ATELIER_FACILITATORS` staan. Zolang die lijst leeg is, komt niemand via Access
    er dus in, en dat is het veilige verzuim.
    """
    if not is_afgeschermd(request):
        return True
    return bezoeker_van(request).strip().lower() in FACILITATORS


def is_afgeschermd(request: Request) -> bool:
    """Staat er een geverifieerde identiteit achter dit verzoek?

    Zolang dat niet zo is, deelt iedereen hetzelfde budget en kan iedereen elke
    identiteit claimen door een header mee te sturen. Dat hoort de bezoeker te zien
    en niet alleen de bouwer -- het atelier leert per slot van rekening dat je moet
    kunnen nagaan waar iets vandaan komt.
    """
    return bool(request.headers.get("cf-access-authenticated-user-email"))


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
                "storing": lees_storingsbanner(),
                "afgeschermd": is_afgeschermd(request)}

    def zoek_module(module_id: str):
        map_ = modules_dir / module_id
        if not map_.is_dir():
            return None, f"Module '{module_id}' bestaat niet."
        try:
            return schema.lees(map_), None
        except schema.ModuleFout as fout:
            return None, str(fout)

    # --------------------------------------------------------- landing
    @app.get("/", response_class=HTMLResponse)
    async def landing(request: Request):
        modules, _ = schema.lees_alle(modules_dir)
        gez = await mid.gezondheid()
        ctx = await omhulsel(request)
        ctx.update(acten=ACTEN, stats={
            "modules": sum(1 for m in modules if m.gepubliceerd),
            "diensten": 20,
            "fragmenten": "924",
            "modellen_gb": "77 GB",
            "conserven": gez.get("conserven", 0),
        })
        return sjablonen.html("landing.html", ctx)

    # ------------------------------------------------------------- route
    @app.get("/start", response_class=HTMLResponse)
    async def start(request: Request):
        """Het keuzemenu. Twee doelgroepen, twee routes, twee eindproducten."""
        modules, _ = schema.lees_alle(modules_dir)
        zichtbaar = [m for m in modules if m.gepubliceerd]
        keuzes = []
        for r in ROUTES:
            hoort_erbij = [m for m in zichtbaar if m.spoor in r["sporen"]]
            keuzes.append({**r, "aantal": len(hoort_erbij),
                           "minuten": sum(m.duur_min for m in hoort_erbij),
                           "beurten": sum(m.beurten for m in hoort_erbij)})
        ctx = await omhulsel(request)
        ctx.update(keuzes=keuzes)
        return sjablonen.html("start.html", ctx)

    @app.get("/route", response_class=HTMLResponse)
    async def route(request: Request, voor: str = ""):
        modules, _ = schema.lees_alle(modules_dir)
        zichtbaar = [m for m in modules if m.gepubliceerd]

        # Zonder geldige keuze tonen we alles, met een verwijzing naar het keuzemenu.
        # Een onbekende waarde is geen fout: de route hoort niet te breken op een
        # verkeerd overgetypte link.
        gekozen = next((r for r in ROUTES if r["id"] == voor), None)
        if gekozen:
            zichtbaar = [m for m in zichtbaar if m.spoor in gekozen["sporen"]]
            sporen = tuple((s, t) for s, t in SPOREN if s in gekozen["sporen"])
        else:
            sporen = SPOREN

        per_spoor = {}
        for m in zichtbaar:
            per_spoor.setdefault(m.spoor, []).append(m)
        ctx = await omhulsel(request)
        ctx.update(per_spoor=per_spoor, sporen=sporen, zichtbaar=zichtbaar,
                   gekozen=gekozen, routes=ROUTES)
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
        # Altijd aanroepen, ook bij nul beurten: dit registreert het bezoek. Bij nul
        # beurten reserveert de bemiddelaar niets, dus het kost de bezoeker ook niets.
        reservering_fout = None
        code, body = await mid.reserveer(ctx["bezoeker"], module.id, module.beurten)
        if module.beurten > 0:
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
        code, body = await mid.vraag(bezoeker_van(request), module_id, v.vraag,
                                     voorkeur, module.poc)
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
                  f"Ingevuld door: {ingevuld_door} - Organisatie: {organisatie}", ""]
        for i, (veld, kop, hulp) in enumerate(KAARTVELDEN, 1):
            regels += [f"## {i}. {kop}", hulp, "", (waarden[veld] or "").strip(), ""]
        regels += ["---", "",
                   "Ingevuld in het Leeratelier op orin3. Indicatief, geen operationeel advies."]
        naam = "".join(c if c.isalnum() or c in "-_" else "-" for c in toepassing.lower())[:60]
        return PlainTextResponse(
            "\n".join(regels), media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="beheerkaart-{naam}.md"'})

    # ------------------------------------------------------ besluitkaart
    @app.get("/besluitkaart", response_class=HTMLResponse)
    async def besluitkaart(request: Request):
        ctx = await omhulsel(request)
        ctx.update(velden=BESLUITVELDEN)
        return sjablonen.html("besluitkaart.html", ctx)

    @app.post("/besluitkaart/export")
    async def besluitkaart_export(
        toepassing: str = Form(...), ingevuld_door: str = Form(""),
        organisatie: str = Form(""), besluit: str = Form(""), belofte: str = Form(""),
        mis: str = Form(""), rekening: str = Form(""), eigenaar: str = Form(""),
        stoppen: str = Form(""),
    ):
        waarden = {"besluit": besluit, "belofte": belofte, "mis": mis,
                   "rekening": rekening, "eigenaar": eigenaar, "stoppen": stoppen}
        regels = [f"# Besluitkaart - {toepassing}", "",
                  f"Ingevuld door: {ingevuld_door} - Organisatie: {organisatie}", ""]
        for i, (veld, kop, hulp) in enumerate(BESLUITVELDEN, 1):
            regels += [f"## {i}. {kop}", hulp, "", (waarden[veld] or "").strip(), ""]
        regels += ["---", "",
                   "Ingevuld in het Leeratelier op orin3. Indicatief, geen operationeel advies."]
        naam = "".join(c if c.isalnum() or c in "-_" else "-" for c in toepassing.lower())[:60]
        return PlainTextResponse(
            "\n".join(regels), media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="besluitkaart-{naam}.md"'})

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
        # 404 en geen 403: een bezoeker hoeft niet te weten dat deze pagina bestaat.
        if not mag_facilitator(request):
            ctx = await omhulsel(request)
            ctx.update(kop="Deze pagina bestaat niet",
                       melding="Kijk op de route of je de module zoekt die je bedoelde.")
            return sjablonen.html("fout.html", ctx, status_code=404)
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
