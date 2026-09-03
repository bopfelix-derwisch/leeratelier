# Leerbemiddelaar :8794 — WP-05 — 2026-09-03

Het eerste stuk van het atelier dat echt gebouwd is. De bemiddelaar bestaat omdat één
32B-model breekt zodra er meer dan één bezoeker tegelijk iets vraagt, en omdat het
atelier permanent en **onbewaakt** open staat.

**Draait:** `atelier-bemiddelaar.service`, enabled en active, gebonden op
`127.0.0.1:8794` en niet publiek bereikbaar.

---

## 1. De klaar-als, gemeten

De backlog eist: acht gelijktijdige verzoeken krijgen allemaal binnen twee seconden
een status, niemand valt stil, het budget wordt correct afgeboekt, en bij een gestopt
model valt alles netjes terug.

Gedraaid tegen het **echte klasmodel**, niet tegen een nabootsing:

```
acht verzoeken ingediend in 0,25 s          (eis: < 2 s)
  posities 0,0,1,1,2,2,3,3 · schattingen 1-5 s
alle acht beantwoord na 9 s · latency 2,9 - 4,1 s
budget: 19 van 20 per bezoeker over, 292 van 300 voor de dag
```

Acht verzoeken, acht afboekingen, geen enkele te veel of te weinig. De schatting
(1–5 s) lag in dezelfde orde als de werkelijkheid (2,9–4,1 s).

## 2. De degradatieladder

| trede | bron | wanneer | getoetst |
|---|---|---|---|
| 1 | `cache` | identieke genormaliseerde vraag binnen de bewaartermijn | test + live |
| 2 | `klas` | standaard, klasmodel op :8081 | **live** |
| 3 | `show` | module vraagt erom, of het klasmodel is weg | **live** |
| 4 | `conserf` | budget op, rij vol, of geen enkel model bereikbaar | test |
| 5 | — | licht pad blijft open, melding over middernacht | test |

**Trede 3 live getoetst** met het verificatiecommando uit de backlog
(`systemctl stop llama-klasmodel`):

```
klasmodel: weg | showmodel: actief | storingsmodus: false
status=klaar  bron=show  model=Qwen2.5-32B-Instruct  beurten=1
```

De bezoeker krijgt gewoon antwoord. Het enige verschil is het bronlabel en dat het
trager is — precies zoals bedoeld.

**Trede 4 is met tests getoetst, niet live**, en dat is een bewuste keuze. Om conserven
uit te lokken moeten *beide* modellen weg zijn, en het showmodel op :8080 is het model
van Derwisch. Dat stilleggen om een eigen werkpakket af te vinken is niet in verhouding.
Twee tests dekken het: één waarin beide modellen onbereikbaar zijn en het antwoord uit
een conserf komt zonder dat het een beurt kost, en één waarin er ook geen conserf is en
de bezoeker een uitleg krijgt in plaats van een leeg scherm.

Er staan nu **vijf echte conserven** voor K4, gegenereerd uit de ijkset-antwoorden van
Qwen3-8B uit WP-03 — geen bedachte teksten maar wat het gekozen klasmodel werkelijk
antwoordde.

## 3. Wat er gebouwd is

```
gateway/instellingen.py   config lezen; geen enkele waarde staat in code
gateway/db.py             sqlite, vier tabellen, verbinding per thread
gateway/budget.py         dag- en persoonsbudget, reserveren, afboeken
gateway/cache.py          trede 1, met terughoudend normaliseren
gateway/conserven.py      trede 4, leest content/conserven/
gateway/logboek.py        logboek + meldingen, 90 dagen, opruimtaak
gateway/modellen.py       praten met llama.cpp, en weten of het er is
gateway/wachtrij.py       rij per model, werkers, wachttijdschatting
gateway/main.py           FastAPI, de ladder, de zes endpoints
tests/test_bemiddelaar.py 21 tests
```

Alle zes de endpoints uit `gateway/README.md` zijn er: `POST /v1/vraag`,
`GET /v1/taak/{id}`, `GET /v1/budget/{id}`, `POST /v1/reserveer`, `GET /v1/gezondheid`,
`POST /v1/melding`. Plus `GET /health` voor systemd en sysmonitor.

### Drie ontwerpkeuzes die uitleg verdienen

**De reset om middernacht is geen taak maar een sleutel.** Verbruik wordt geboekt per
`(bezoeker, datum)`. Een nieuwe dag is een nieuwe rij die op nul begint. Er is dus geen
cron die kan missen — belangrijk voor een dienst die onbewaakt draait, want een gemiste
reset zou het budget op nul vastzetten tot iemand het merkt.

**Reserveren telt voor de persoon, niet voor de dag.** Wie een module opent, legt zijn
eigen beurten vast zodat hij niet halverwege strandt (regel 1 van het modulecontract).
Maar het dagbudget gaat pas omlaag bij echt verbruik: iemand die een module opent en
weer weggaat, kost het atelier niets.

**Een storing kost de bezoeker geen budget.** Valt het antwoord terug op een conserf,
dan gaat de reservering terug. Wie betaalt voor een storing die hij niet veroorzaakte,
leert het verkeerde.

## 4. Wat hier misging

**Ik schreef in de docstring van `db.py` dat elke aanroeper een eigen verbinding krijgt,
en bouwde toen één gedeelde.** Sqlite weigert een verbinding te gebruiken vanuit een
andere thread dan waarin hij gemaakt is, en FastAPI draait de schrijvers via
`asyncio.to_thread` in een threadpool. Tien tests vielen om met
`SQLite objects created in a thread can only be used in that same thread`.

Wat dit leerzaam maakt: dit was **niet** zichtbaar geweest met één gebruiker. De fout
komt pas boven bij gelijktijdigheid, en precies daarvoor bestaat deze dienst. De
docstring beschreef het goede ontwerp; de code deed iets anders. Nu is er een
`Verbinding`-klasse die per thread een eigen sqlite-verbinding opent naar hetzelfde
bestand, met WAL zodat lezers niet op de schrijver wachten.

**Het budget was niet atomair.** `reserveer` en `boek_af` lazen eerst de stand en
schreven daarna — twee threads lezen dan dezelfde waarde en een van de twee updates
gaat verloren. Bij acht gelijktijdige verzoeken is dat geen theorie. De klemmende
voorwaarde staat nu in de `UPDATE` zelf:

```sql
UPDATE verbruik SET gereserveerd = gereserveerd
     + MIN(?, MAX(0, ? - beurten - gereserveerd))
 WHERE bezoeker_id=? AND datum=?
```

Twee tests lokken het uit met twintig parallelle threads tegen een budget van drie.

**Het logboek noteerde de laddertrede twee keer.** `bron` en `model` bevatten allebei
"klas" of "show". Het logboek is straks het materiaal voor module K6, en daar zegt
`Qwen3-8B` meer dan `klas`. Nu staat de modelnaam in `model` en de trede in `bron`.

## 5. Wat er niet in zit, met opzet

- **Geen streaming.** Pollen op `/v1/taak/{id}` is genoeg en veel eenvoudiger. Staat zo
  in het contract.
- **Geen prioriteiten of rollen.** Het atelier heeft één soort bezoeker.
- **Geen eigen inlog.** Identiteit komt uit de Cloudflare Access-header, en dat is WP-07.
- **Geen vectordatabase.** De RAG-kant blijft zoals hij is.

## 6. Herhalen

```bash
python3 -m pytest tests/test_bemiddelaar.py -q
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -m json.tool
systemctl stop llama-klasmodel   # trede 3: valt terug op het showmodel
systemctl start llama-klasmodel
```

## 7. Wat hierna nodig is

- **WP-06 portaal** is de enige klant van deze dienst. Tot dat er is, is de bemiddelaar
  alleen met `curl` te bedienen.
- **WP-07 toegang**: `bezoeker_id` wordt nu door de aanroeper meegegeven. Dat is
  bruikbaar voor tests maar niet voor productie; het moet uit de Access-header komen,
  en de bemiddelaar mag pas open als het portaal ervoor staat.
- **WP-08 sysmonitor** kan `/v1/gezondheid` nu uitlezen: alle zes de drempels uit plan
  §8 hebben er een veld (`wachtrij_diepte`, `dagbudget_verbruikt_pct`,
  `p95_latency_ms`, `rag_index_leeftijd_dagen`, `klasmodel`, `open_meldingen`).
