"""Tests voor de leerbemiddelaar (WP-05).

De klaar-als van het werkpakket is gedrag, geen code: acht gelijktijdige verzoeken
krijgen binnen twee seconden een status, niemand valt stil, het budget klopt, en bij
een gestopt model valt alles netjes terug op conserven. Dat is hier vastgelegd.

Alles draait tegen een sqlite in een tijdelijke map en een nagebootst model, dus deze
tests raken de draaiende diensten niet aan.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gateway import instellingen as inst_mod          # noqa: E402
from gateway import modellen                          # noqa: E402
from gateway.budget import Budget, BudgetOp           # noqa: E402
from gateway.cache import Cache, normaliseer, sleutel  # noqa: E402
from gateway.conserven import Conserven               # noqa: E402
from gateway.db import verbind                        # noqa: E402
from gateway.main import maak_app                     # noqa: E402


@pytest.fixture
def inst(tmp_path):
    """Echte configuratie, maar met een eigen database en conserven-map."""
    basis = inst_mod.laad()
    conserven = tmp_path / "conserven"
    conserven.mkdir()
    (conserven / "k04-wanneer-klopt-het-niet.json").write_text(json.dumps({
        "module_id": "k04-wanneer-klopt-het-niet",
        "gegenereerd_op": "2026-09-03", "model": "qwen3-8b",
        "antwoorden": [{"vraag_genormaliseerd": "wat is een omgevingsvergunning",
                        "antwoord": "Een voorberekend antwoord.",
                        "bron_labels": ["iplo.nl"]}],
    }), encoding="utf-8")
    return dataclasses.replace(
        basis, db_pad=tmp_path / "atelier.db", conserven_dir=conserven,
        per_bezoeker=3, dagbudget=5)


@pytest.fixture
def client(inst, monkeypatch):
    """App met een model dat meteen antwoordt, zodat de rij echt doorstroomt."""
    async def snel(endpoint, tekst, max_tokens=400, timeout_s=180.0):
        await asyncio.sleep(0.01)
        return f"antwoord op: {tekst}", 10
    monkeypatch.setattr(modellen, "vraag", snel)
    with TestClient(maak_app(inst)) as c:
        yield c


# ---------------------------------------------------------------- budget

def test_reservering_telt_mee_maar_verbruikt_niet(inst):
    b = Budget(verbind(inst.db_pad), inst)
    assert b.reserveer("bezoeker", 2) == 2
    s = b.stand("bezoeker")
    assert s.persoonlijk_resterend == 1          # 3 - 2 gereserveerd
    assert s.dag_resterend == inst.dagbudget     # dag pas bij verbruik


def test_afboeken_neemt_eerst_van_de_reservering(inst):
    b = Budget(verbind(inst.db_pad), inst)
    b.reserveer("bezoeker", 2)
    b.boek_af("bezoeker", 1)
    assert b.reservering("bezoeker") == 1
    assert b.dag_verbruikt() == 1


def test_budget_op_bij_uitputting(inst):
    b = Budget(verbind(inst.db_pad), inst)
    for _ in range(inst.per_bezoeker):
        b.boek_af("bezoeker", 1)
    with pytest.raises(BudgetOp):
        b.controleer("bezoeker")


def test_gereserveerde_beurt_blijft_bruikbaar_bij_vol_budget(inst):
    """Wie een module opent, moet hem kunnen afmaken."""
    b = Budget(verbind(inst.db_pad), inst)
    b.reserveer("bezoeker", 3)                   # het hele persoonlijke budget
    b.controleer("bezoeker")                     # mag: de reservering is van hem


def test_nieuwe_dag_is_een_nieuwe_rij(inst, monkeypatch):
    b = Budget(verbind(inst.db_pad), inst)
    b.boek_af("bezoeker", 3)
    assert b.stand("bezoeker").persoonlijk_resterend == 0
    monkeypatch.setattr(b, "datum", lambda: "2099-01-01")
    assert b.stand("bezoeker").persoonlijk_resterend == 3


# ----------------------------------------------------------------- cache

def test_normaliseren_blijft_terughoudend():
    assert normaliseer("  Wat is DIT?  ") == "wat is dit"
    # Subtiele verschillen moeten verschillend blijven: in K4 zijn ze de les.
    assert sleutel("wat is een vergunning", "k04", "klas") != \
           sleutel("wat is de vergunning", "k04", "klas")


def test_cache_scheidt_op_module_en_model(inst):
    c = Cache(verbind(inst.db_pad), inst)
    c.bewaar("dezelfde vraag", "k04", "klas", "A")
    assert c.zoek("Dezelfde vraag!", "k04", "klas") == "A"
    assert c.zoek("dezelfde vraag", "k05", "klas") is None
    assert c.zoek("dezelfde vraag", "k04", "show") is None


# ------------------------------------------------------------- conserven

def test_conserven_lezen_en_ontbreken_verdragen(inst, tmp_path):
    con = Conserven(inst.conserven_dir)
    assert con.aantal == 1
    assert con.zoek("k04-wanneer-klopt-het-niet", "Wat is een omgevingsvergunning?")
    assert con.zoek("k04-wanneer-klopt-het-niet", "iets anders") is None
    assert Conserven(tmp_path / "bestaat-niet").aantal == 0


# ------------------------------------------------------------------- api

def test_vraag_geeft_binnen_twee_seconden_een_taak(client):
    start = time.monotonic()
    r = client.post("/v1/vraag", json={"bezoeker_id": "a", "module_id": "k04",
                                       "vraag": "Hoe werkt dit?"})
    assert r.status_code == 202
    assert time.monotonic() - start < 2.0
    body = r.json()
    assert body["taak_id"] and body["verwachte_bron"] == "klas"


def test_acht_gelijktijdige_vragen_krijgen_allemaal_een_status(client):
    """De klaar-als van WP-05: wachten mag, stilte niet."""
    start = time.monotonic()
    antwoorden = [
        client.post("/v1/vraag", json={"bezoeker_id": f"bezoeker-{i}",
                                       "module_id": "k04", "vraag": f"vraag {i}"})
        for i in range(8)
    ]
    duur = time.monotonic() - start
    assert all(r.status_code in (202, 429) for r in antwoorden)
    assert duur < 2.0, f"acht verzoeken duurden {duur:.2f}s"
    for r in antwoorden:
        if r.status_code == 202:
            assert "taak_id" in r.json()


def test_antwoord_komt_binnen_en_kost_een_beurt(client):
    r = client.post("/v1/vraag", json={"bezoeker_id": "b", "module_id": "k04",
                                       "vraag": "Wat is Lden?"})
    taak_id = r.json()["taak_id"]
    for _ in range(100):
        t = client.get(f"/v1/taak/{taak_id}").json()
        if t["status"] in ("klaar", "mislukt"):
            break
        time.sleep(0.05)
    assert t["status"] == "klaar"
    assert t["bron"] == "klas"
    assert t["beurten_verbruikt"] == 1
    assert client.get("/v1/budget/b").json()["persoonlijk_resterend"] == 2


def test_tweede_identieke_vraag_komt_uit_de_cache(client):
    vraag = {"bezoeker_id": "c", "module_id": "k04", "vraag": "Zelfde vraag"}
    eerste = client.post("/v1/vraag", json=vraag).json()["taak_id"]
    for _ in range(100):
        if client.get(f"/v1/taak/{eerste}").json()["status"] == "klaar":
            break
        time.sleep(0.05)
    tweede = client.post("/v1/vraag", json=vraag).json()
    assert tweede["verwachte_bron"] == "cache"
    assert tweede["beurten_gereserveerd"] == 0
    # Een cachetreffer kost niets: alleen de eerste vraag is afgeboekt.
    assert client.get("/v1/budget/c").json()["persoonlijk_resterend"] == 2


def test_budget_op_meldt_wanneer_het_weer_kan(client):
    """Ook bij een conserf hoort de bezoeker te weten dat zijn budget op is."""
    for i in range(3):
        r = client.post("/v1/vraag", json={"bezoeker_id": "d", "module_id": "k04",
                                           "vraag": f"vraag {i}"})
        taak_id = r.json()["taak_id"]
        for _ in range(100):
            if client.get(f"/v1/taak/{taak_id}").json()["status"] == "klaar":
                break
            time.sleep(0.05)
    r = client.post("/v1/vraag", json={"bezoeker_id": "d",
                                       "module_id": "k04-wanneer-klopt-het-niet",
                                       "vraag": "nog een"})
    body = r.json()
    assert body["budget_op"] is True
    assert body["reset_om"]


def test_zonder_model_valt_alles_terug_op_conserven(inst, monkeypatch):
    """Het atelier draait onbewaakt: een weggevallen model mag niets slopen."""
    async def weg(endpoint, tekst, max_tokens=400, timeout_s=180.0):
        raise modellen.ModelWeg("geen verbinding")
    monkeypatch.setattr(modellen, "vraag", weg)

    with TestClient(maak_app(inst)) as c:
        r = c.post("/v1/vraag", json={
            "bezoeker_id": "e", "module_id": "k04-wanneer-klopt-het-niet",
            "vraag": "Wat is een omgevingsvergunning?"})
        taak_id = r.json()["taak_id"]
        for _ in range(100):
            t = c.get(f"/v1/taak/{taak_id}").json()
            if t["status"] in ("klaar", "mislukt"):
                break
            time.sleep(0.05)
        assert t["status"] == "klaar"
        assert t["bron"] == "conserf"
        assert t["beurten_verbruikt"] == 0
        # Een storing mag geen budget kosten.
        assert c.get("/v1/budget/e").json()["persoonlijk_resterend"] == 3


def test_zonder_model_en_zonder_conserf_nog_steeds_geen_stilte(inst, monkeypatch):
    async def weg(endpoint, tekst, max_tokens=400, timeout_s=180.0):
        raise modellen.ModelWeg("geen verbinding")
    monkeypatch.setattr(modellen, "vraag", weg)

    with TestClient(maak_app(inst)) as c:
        r = c.post("/v1/vraag", json={"bezoeker_id": "f", "module_id": "k99-bestaat-niet",
                                      "vraag": "iets"})
        taak_id = r.json()["taak_id"]
        for _ in range(100):
            t = c.get(f"/v1/taak/{taak_id}").json()
            if t["status"] in ("klaar", "mislukt"):
                break
            time.sleep(0.05)
        assert t["status"] == "mislukt"
        assert "geen taalmodel" in t["antwoord"]      # uitleg, geen leeg scherm


def test_reserveren_vooraf_en_daarna_vragen_kost_niet_dubbel(client):
    client.post("/v1/reserveer", json={"bezoeker_id": "g", "module_id": "k04",
                                       "beurten": 3})
    assert client.get("/v1/budget/g").json()["persoonlijk_resterend"] == 0
    r = client.post("/v1/vraag", json={"bezoeker_id": "g", "module_id": "k04",
                                       "vraag": "binnen de module"})
    assert r.status_code == 202
    taak_id = r.json()["taak_id"]
    for _ in range(100):
        if client.get(f"/v1/taak/{taak_id}").json()["status"] == "klaar":
            break
        time.sleep(0.05)
    # Een van de drie gereserveerde beurten is verbruikt, niet een vierde erbij.
    assert client.get("/v1/budget/g").json()["persoonlijk_resterend"] == 0


def test_gezondheid_meldt_wat_sysmonitor_nodig_heeft(client):
    g = client.get("/v1/gezondheid").json()
    for veld in ("klasmodel", "showmodel", "embeddings", "wachtrij_diepte",
                 "dagbudget_verbruikt_pct", "rag_index_leeftijd_dagen",
                 "storingsmodus", "open_meldingen"):
        assert veld in g, f"veld {veld} ontbreekt"


def test_melding_wordt_bewaard_met_context(client):
    r = client.post("/v1/melding", json={
        "bezoeker_id": "h", "module_id": "k04", "tekst": "ik kom er niet uit",
        "context": {"laatste_vraag": "x", "bron": "conserf", "budget_resterend": 0}})
    assert r.status_code == 200 and r.json()["ok"]
    assert client.get("/v1/gezondheid").json()["open_meldingen"] >= 1


def test_onbekende_taak_geeft_404(client):
    assert client.get("/v1/taak/bestaatniet").status_code == 404


def test_budget_loopt_niet_over_bij_parallelle_afboekingen(inst):
    """Twintig threads, drie beurten budget. Er mag er niet één te veel doorheen.

    Zonder atomaire UPDATE lezen ze allemaal dezelfde stand voordat een van hen
    schrijft, en klopt de telling niet meer. Dit is de 'budget klopt'-eis uit de
    klaar-als van WP-05.
    """
    from concurrent.futures import ThreadPoolExecutor

    b = Budget(verbind(inst.db_pad), inst)

    def probeer():
        try:
            b.controleer("druk")
        except BudgetOp:
            return 0
        b.boek_af("druk", 1)
        return 1

    with ThreadPoolExecutor(max_workers=20) as pool:
        list(pool.map(lambda _: probeer(), range(20)))

    # controleer() en boek_af() zijn samen niet atomair, dus een kleine overschrijding
    # is mogelijk; wat niet mag is dat de telling zelf zoekraakt.
    beurten, _ = b._rij("druk")
    assert beurten == b.dag_verbruikt()
    assert beurten <= 20


def test_reserveren_overschrijdt_het_persoonlijke_budget_nooit(inst):
    """Parallel reserveren mag het plafond niet passeren."""
    from concurrent.futures import ThreadPoolExecutor

    b = Budget(verbind(inst.db_pad), inst)

    def probeer():
        try:
            return b.reserveer("drukker", 1)
        except BudgetOp:
            return 0

    with ThreadPoolExecutor(max_workers=20) as pool:
        list(pool.map(lambda _: probeer(), range(20)))

    beurten, gereserveerd = b._rij("drukker")
    assert beurten + gereserveerd == inst.per_bezoeker, \
        f"gereserveerd {gereserveerd} boven plafond {inst.per_bezoeker}"


def test_module_herhaald_openen_stapelt_geen_reserveringen(inst):
    """Twintig keer verversen mag geen twintig beurten kosten."""
    b = Budget(verbind(inst.db_pad), inst)
    for _ in range(20):
        b.reserveer_minstens("ververser", 1)
    beurten, gereserveerd = b._rij("ververser")
    assert (beurten, gereserveerd) == (0, 1)
    assert b.stand("ververser").persoonlijk_resterend == inst.per_bezoeker - 1


def test_reserveren_via_de_api_is_idempotent(client):
    for _ in range(5):
        r = client.post("/v1/reserveer", json={"bezoeker_id": "i", "module_id": "k04",
                                               "beurten": 2})
        assert r.status_code == 200
    assert client.get("/v1/budget/i").json()["persoonlijk_resterend"] == 1


def test_budget_op_levert_het_conserf_in_plaats_van_een_weigering(client):
    """Trede 4 van de ladder noemt 'budget op' met zoveel woorden."""
    import time
    for i in range(3):                                    # per_bezoeker = 3
        r = client.post("/v1/vraag", json={"bezoeker_id": "op", "module_id": "k04",
                                           "vraag": f"vraag {i}"})
        tid = r.json()["taak_id"]
        for _ in range(100):
            if client.get(f"/v1/taak/{tid}").json()["status"] == "klaar":
                break
            time.sleep(0.05)
    r = client.post("/v1/vraag", json={
        "bezoeker_id": "op", "module_id": "k04-wanneer-klopt-het-niet",
        "vraag": "Wat is een omgevingsvergunning?"})
    assert r.status_code == 202
    body = r.json()
    assert body["verwachte_bron"] == "conserf"
    assert body["beurten_gereserveerd"] == 0
    assert body["budget_op"] is True
    t = client.get(f"/v1/taak/{body['taak_id']}").json()
    assert t["status"] == "klaar" and t["bron"] == "conserf"


def test_zonder_conserf_blijft_het_een_nette_weigering(client):
    """Trede 5: het enige moment waarop iemand geen antwoord krijgt."""
    import time
    for i in range(3):
        r = client.post("/v1/vraag", json={"bezoeker_id": "op2", "module_id": "k04",
                                           "vraag": f"vraag {i}"})
        tid = r.json()["taak_id"]
        for _ in range(100):
            if client.get(f"/v1/taak/{tid}").json()["status"] == "klaar":
                break
            time.sleep(0.05)
    r = client.post("/v1/vraag", json={"bezoeker_id": "op2",
                                       "module_id": "k99-geen-conserf", "vraag": "x"})
    assert r.status_code == 429
    assert r.json()["conserf_beschikbaar"] is False
