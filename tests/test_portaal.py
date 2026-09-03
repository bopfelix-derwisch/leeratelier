"""Tests voor het atelier-portaal (WP-06).

De klaar-als: een testbezoeker doorloopt een module, verbruikt budget, krijgt bij
uitputting een conserf, en dat is terug te vinden in het logboek. Dat wordt hier
end-to-end gedraaid -- portaal en bemiddelaar samen, met een nagebootst model, zodat
de draaiende diensten er niet aan te pas komen.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import schema                                # noqa: E402
from app.main import maak_app as maak_portaal         # noqa: E402
from gateway import instellingen as inst_mod          # noqa: E402
from gateway import modellen                          # noqa: E402
from gateway.main import maak_app as maak_bemiddelaar  # noqa: E402

WORTEL = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------- modulecontract

def schrijf_module(map_: Path, **overschrijf) -> Path:
    fm = {"id": map_.name, "titel": "Een module", "spoor": "basis", "volgorde": 10,
          "competenties": "[B1]", "duur_min": 10, "beurten": 1, "modellen": "[klas]",
          "status": "gepubliceerd", "wat_ging_mis": "true", "bewijs": "iets"}
    fm.update({k: v for k, v in overschrijf.items() if k != "tekst"})
    tekst = overschrijf.get("tekst", "# Kop\n\nInhoud.\n\n## Wat hier misging\n\nDit ging mis.\n")
    map_.mkdir(parents=True, exist_ok=True)
    kop = "\n".join(f"{k}: {v}" for k, v in fm.items())
    (map_ / "module.md").write_text(f"---\n{kop}\n---\n\n{tekst}", encoding="utf-8")
    return map_


def test_module_zonder_wat_ging_mis_rendert_niet(tmp_path):
    """Regel 2 van het modulecontract, met opzet streng."""
    map_ = schrijf_module(tmp_path / "k11-test", tekst="# Kop\n\nGeen sectie hier.\n")
    with pytest.raises(schema.ModuleFout, match="Wat hier misging"):
        schema.lees(map_)


def test_concept_mag_de_sectie_missen(tmp_path):
    """Een concept is nog onaf -- maar bereikt ook niemand."""
    map_ = schrijf_module(tmp_path / "k12-test", status="concept",
                          tekst="# Kop\n\nNog niets.\n")
    assert schema.lees(map_).gepubliceerd is False


def test_id_moet_gelijk_zijn_aan_de_mapnaam(tmp_path):
    map_ = schrijf_module(tmp_path / "k13-test", id="iets-anders")
    with pytest.raises(schema.ModuleFout, match="wijkt af van de mapnaam"):
        schema.lees(map_)


def test_ontbrekend_veld_wordt_benoemd(tmp_path):
    map_ = tmp_path / "k14-test"
    map_.mkdir()
    (map_ / "module.md").write_text("---\nid: k14-test\ntitel: x\n---\n\n# Kop\n", encoding="utf-8")
    with pytest.raises(schema.ModuleFout, match="frontmatter mist"):
        schema.lees(map_)


def test_een_kapotte_module_sloopt_de_route_niet(tmp_path):
    schrijf_module(tmp_path / "k15-goed")
    schrijf_module(tmp_path / "k16-stuk", tekst="# Kop\n\nGeen sectie.\n")
    modules, fouten = schema.lees_alle(tmp_path)
    assert [m.id for m in modules] == ["k15-goed"]
    assert len(fouten) == 1 and "k16-stuk" in fouten[0]


def test_echte_modules_voldoen_aan_het_contract():
    """De modules in deze repo moeten renderen. Anders is de route stuk."""
    modules, fouten = schema.lees_alle(WORTEL / "content" / "modules")
    assert not fouten, f"modules die niet renderen: {fouten}"
    assert any(m.gepubliceerd for m in modules), "geen enkele gepubliceerde module"


# ------------------------------------------------------------------ end-to-end

@pytest.fixture
def keten(tmp_path, monkeypatch):
    """Portaal plus bemiddelaar, met een nagebootst model. Geen echte diensten."""
    async def snel(endpoint, tekst, max_tokens=400, timeout_s=180.0):
        await asyncio.sleep(0.01)
        return f"Antwoord op: {tekst}", 12
    monkeypatch.setattr(modellen, "vraag", snel)

    conserven = tmp_path / "conserven"
    conserven.mkdir()
    (conserven / "k00-proefmodule.json").write_text(json.dumps({
        "module_id": "k00-proefmodule", "gegenereerd_op": "2026-09-03", "model": "Qwen3-8B",
        "antwoorden": [{"vraag_genormaliseerd": "een vraag", "antwoord": "Voorberekend.",
                        "bron_labels": ["proef"]}]}), encoding="utf-8")

    inst = dataclasses.replace(
        inst_mod.laad(), db_pad=tmp_path / "atelier.db", conserven_dir=conserven,
        per_bezoeker=2, dagbudget=10)

    with TestClient(maak_bemiddelaar(inst)) as bem:
        # Het portaal praat met de bemiddelaar via httpx; die wordt hier omgeleid
        # naar de testclient, zodat er geen echte poort aan te pas komt.
        import app.render as render_mod

        class DirecteClient:
            """httpx-vervanger die rechtstreeks op de bemiddelaar-testclient uitkomt.

            De aanroepen gaan via `asyncio.to_thread`: de testclient van Starlette
            weigert aangeroepen te worden vanuit de eventloop-thread waarin het
            portaal draait.
            """

            def __init__(self, *a, **kw): pass
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False

            async def get(self, url, **kw):
                return await asyncio.to_thread(bem.get, url.replace("http://bem", ""))

            async def post(self, url, json=None, **kw):
                return await asyncio.to_thread(
                    lambda: bem.post(url.replace("http://bem", ""), json=json))

        monkeypatch.setattr(render_mod.httpx, "AsyncClient", DirecteClient)
        with TestClient(maak_portaal(bemiddelaar_basis="http://bem")) as portaal:
            yield portaal, inst


def test_route_toont_alleen_gepubliceerde_modules(keten):
    portaal, _ = keten
    html = portaal.get("/").text
    assert "k00-proefmodule" in html
    assert "k04-wanneer-klopt-het-niet" not in html      # concept: onzichtbaar


def test_facilitator_ziet_de_concepten_wel(keten):
    portaal, _ = keten
    html = portaal.get("/facilitator").text
    assert "k04-wanneer-klopt-het-niet" in html
    assert "concept" in html


def test_modulepagina_toont_budgetmeter_en_reserveert(keten):
    portaal, _ = keten
    html = portaal.get("/module/k00-proefmodule").text
    assert "beurten vandaag" in html                     # budgetmeter op de pagina
    assert "Proefmodule" in html
    # De module kost 1 beurt; die is bij het openen gereserveerd.
    assert "nog <b>1</b>" in html or "nog <b>0</b>" in html


def test_begeleiding_wordt_nooit_geserveerd(keten):
    portaal, _ = keten
    for pad in ("/module/k04-wanneer-klopt-het-niet/begeleiding",
                "/opdracht/k04-wanneer-klopt-het-niet/begeleiding"):
        assert portaal.get(pad).status_code in (404, 405)


def test_hele_keten_vraag_tot_logboek(keten):
    """De klaar-als van WP-06, end-to-end."""
    portaal, inst = keten
    portaal.get("/module/k00-proefmodule")
    r = portaal.post("/module/k00-proefmodule/vraag", json={"vraag": "Wat is dit?"})
    assert r.status_code == 200
    taak_id = r.json()["taak_id"]

    import time
    for _ in range(100):
        t = portaal.get(f"/taak/{taak_id}").json()
        if t["status"] in ("klaar", "mislukt"):
            break
        time.sleep(0.05)
    assert t["status"] == "klaar"
    assert t["bron"] == "klas"
    assert t["beurten_verbruikt"] == 1

    # Terug te vinden in het logboek.
    con = sqlite3.connect(str(inst.db_pad))
    rij = con.execute("SELECT module_id, bron, beurten, gelukt FROM logboek "
                      "ORDER BY id DESC LIMIT 1").fetchone()
    assert rij == ("k00-proefmodule", "klas", 1, 1)


def test_bij_uitputting_verwijst_het_portaal_naar_het_conserf(keten):
    portaal, _ = keten
    import time
    for i in range(2):                                    # per_bezoeker = 2
        r = portaal.post("/module/k00-proefmodule/vraag", json={"vraag": f"vraag {i}"})
        tid = r.json()["taak_id"]
        for _ in range(100):
            if portaal.get(f"/taak/{tid}").json()["status"] == "klaar":
                break
            time.sleep(0.05)
    r = portaal.post("/module/k00-proefmodule/vraag", json={"vraag": "nog een"})
    assert r.status_code == 429
    body = r.json()
    assert body["fout"] == "budget_op"
    assert "voorberekend antwoord" in body["melding"]


def test_vastgelopen_vangt_context(keten):
    portaal, inst = keten
    r = portaal.post("/vastgelopen", data={
        "tekst": "ik snap het niet", "module_id": "k00-proefmodule",
        "laatste_vraag": "wat is dit", "laatste_bron": "klas"})
    assert r.status_code == 200
    con = sqlite3.connect(str(inst.db_pad))
    tekst, ruw = con.execute(
        "SELECT tekst, context FROM meldingen ORDER BY id DESC LIMIT 1").fetchone()
    context = json.loads(ruw)
    assert tekst == "ik snap het niet"
    assert context["laatste_vraag"] == "wat is dit"
    assert context["bron"] == "klas"
    assert "budget_resterend" in context and "klasmodel" in context


def test_beheerkaart_exporteert_markdown(keten):
    portaal, _ = keten
    r = portaal.post("/beheerkaart/export", data={
        "toepassing": "Mijn WFS-koppeling", "ingevuld_door": "Test",
        "mis": "de bron verandert", "signaal": "lege kaart"})
    assert r.status_code == 200
    assert "attachment" in r.headers["content-disposition"]
    assert "beheerkaart-mijn-wfs-koppeling.md" in r.headers["content-disposition"]
    assert "# Beheerkaart - Mijn WFS-koppeling" in r.text
    assert "de bron verandert" in r.text


def test_onbekende_module_geeft_nette_fout(keten):
    portaal, _ = keten
    r = portaal.get("/module/bestaat-niet")
    assert r.status_code == 404
    assert "bestaat niet" in r.text


def test_gezondheid_voor_sysmonitor(keten):
    portaal, _ = keten
    g = portaal.get("/gezondheid").json()
    assert g["portaal"] == "actief"
    assert g["modules_gepubliceerd"] >= 1
    assert g["modules_stuk"] == 0
    assert "keten" in g
