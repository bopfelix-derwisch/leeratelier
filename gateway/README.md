# Leerbemiddelaar :8794 — contract

Bouwopdracht: WP-05. Bindt op `127.0.0.1:8794`. Niet publiek bereikbaar; alleen het portaal praat ermee.

De bemiddelaar is het enige echt nieuwe stuk techniek in dit atelier. Hij bestaat omdat één 32B-model op
ctx 4096 met een ketenlatency van 50–70 s breekt zodra er meer dan één bezoeker tegelijk iets vraagt.

**Kernidee: rantsoeneer het model, niet de deur.** De meeste modules kosten nul modelbeurten. Alleen live
antwoorden zijn schaars, en bij uitputting degradeert de ervaring in plaats van dat iemand geweigerd wordt.

---

## Degradatieladder

Elke vraag doorloopt deze ladder van boven naar beneden. De gekozen trede gaat altijd mee in het antwoord,
want de bezoeker moet kunnen zien waar zijn antwoord vandaan komt — dat is zelf lesmateriaal.

| Trede | Bron | Wanneer |
|---|---|---|
| 1 | `cache` | identieke genormaliseerde vraag binnen de bewaartermijn |
| 2 | `klas` | standaard; klasmodel op :8081 |
| 3 | `show` | alleen als de module erom vraagt (K3) of het klasmodel weg is |
| 4 | `conserf` | budget op, wachtrij vol, of geen enkel model bereikbaar |
| 5 | — | licht pad blijft open; melding "live antwoorden weer beschikbaar na middernacht" |

Trede 4 is geen noodrem maar een volwaardig pad. Het atelier is permanent open en onbewaakt; conserven
zorgen dat de hele route werkt terwijl er geen model draait.

---

## Endpoints

### `POST /v1/vraag`
```json
{ "bezoeker_id": "…", "module_id": "k04-wanneer-klopt-het-niet",
  "vraag": "…", "model_voorkeur": "auto" }
```
`model_voorkeur`: `auto` (standaard) · `klas` · `show`. De module mag dit afdwingen via haar frontmatter.

**202** met een taak. Nooit blokkeren, altijd binnen 2 seconden antwoorden:
```json
{ "taak_id": "…", "positie": 3, "geschat_wachten_s": 95,
  "verwachte_bron": "klas", "beurten_gereserveerd": 1 }
```
**429** als het persoonlijke budget op is:
```json
{ "fout": "budget_op", "reset_om": "2026-09-03T00:00:00+02:00",
  "conserf_beschikbaar": true }
```

### `GET /v1/taak/{taak_id}`
```json
{ "status": "klaar", "positie": null, "antwoord": "…",
  "bron": "klas", "model": "…", "latency_ms": 8421,
  "beurten_verbruikt": 1, "index_leeftijd_dagen": 73 }
```
`status`: `wachtend` · `bezig` · `klaar` · `mislukt`.

`index_leeftijd_dagen` gaat expliciet mee bij elk RAG-antwoord. Module K4 leert bezoekers daarnaar te
vragen; het zou raar zijn als het atelier het zelf verzweeg.

### `GET /v1/budget/{bezoeker_id}`
```json
{ "persoonlijk_resterend": 9, "persoonlijk_totaal": 15,
  "dag_resterend": 88, "dag_totaal": 150, "reset_om": "…" }
```

### `POST /v1/reserveer`
Reserveert vooraf het aantal beurten uit de frontmatter van een module, zodat niemand halverwege een
module zonder budget valt.
```json
{ "bezoeker_id": "…", "module_id": "…" }
→ { "ok": true, "gereserveerd": 3, "vervalt_om": "…" }
```

### `GET /v1/gezondheid`
Gelezen door het portaal (storingsbanner) en door sysmonitor.
```json
{ "klasmodel": "actief", "showmodel": "actief", "embeddings": "actief",
  "wachtrij_diepte": 2, "dagbudget_verbruikt_pct": 41,
  "rag_index_leeftijd_dagen": 73, "storingsmodus": false,
  "open_meldingen": 1 }
```

### `POST /v1/melding`
De "ik kom er niet uit"-knop. Vangt context, want de beheerder is niet altijd bereikbaar.
```json
{ "bezoeker_id": "…", "module_id": "…", "tekst": "…",
  "context": { "laatste_vraag": "…", "bron": "conserf",
               "budget_resterend": 0, "foutmelding": null } }
```

---

## Datamodel — sqlite op `/mnt/nvme/leeratelier/atelier.db`

Niet op `/`: die schijf zit op 81%.

```sql
CREATE TABLE verbruik (          -- budget per bezoeker per dag
  bezoeker_id TEXT, datum TEXT, beurten INTEGER DEFAULT 0,
  gereserveerd INTEGER DEFAULT 0, PRIMARY KEY (bezoeker_id, datum));

CREATE TABLE logboek (           -- besloten: vragen worden gelogd, 90 dagen
  id INTEGER PRIMARY KEY, tijdstip TEXT, bezoeker_id TEXT, module_id TEXT,
  vraag TEXT, model TEXT, bron TEXT, latency_ms INTEGER, beurten INTEGER,
  gelukt INTEGER);

CREATE TABLE cache (
  sleutel TEXT PRIMARY KEY, module_id TEXT, model TEXT,
  antwoord TEXT, aangemaakt TEXT);

CREATE TABLE meldingen (
  id INTEGER PRIMARY KEY, tijdstip TEXT, bezoeker_id TEXT, module_id TEXT,
  tekst TEXT, context TEXT, afgehandeld INTEGER DEFAULT 0);
```

Cachesleutel: `sha256(genormaliseerde_vraag + "|" + module_id + "|" + model)`. Normaliseren = kleine
letters, dubbele spaties weg, leestekens aan de randen weg. Meer niet — te agressief normaliseren laat
verschillende vragen op elkaar lijken, en juist in module K4 zijn subtiele verschillen de les.

Opruimtaak: dagelijks. Logboek ouder dan `logboek.bewaartermijn_dagen`, cache ouder dan
`cache.bewaartermijn_uren`.

---

## Wachtrij

- één werker per model, gelijktijdigheid uit `config/budget.yaml`
- FIFO, geen prioriteit — behalve de reservering voor de begeleide sessie
- positie en schatting binnen 2 s, altijd. **Wachten is acceptabel, stilte niet.**
- bij een wachtrij dieper dan de crit-drempel: nieuwe vragen krijgen meteen een conserf in plaats van een
  plek in de rij

## Wat je hier niet moet bouwen

- geen streaming naar de bezoeker in versie 1 — pollen op `/v1/taak/{id}` is genoeg en veel eenvoudiger
- geen prioriteiten of rollen; het atelier heeft één soort bezoeker
- geen eigen inlog; identiteit komt uit de Cloudflare Access-header
- geen vectordatabase; de RAG-kant blijft zoals hij is
