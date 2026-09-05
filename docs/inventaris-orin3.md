# Bouwmateriaal voor het Leeratelier — inventaris orin3

> Samengesteld 2026-09-02 vanaf orin3 (Jetson AGX Orin 64GB, user bob).
> Diensten/endpoints geverifieerd met `systemctl` en directe HTTP-aanroepen; POC-lijsten opgehaald
> uit de **live publieke pagina's** en de OpenAPI-schema's van de draaiende apps.
> **Leerwaarde, leerlijnen en doelgroepen zijn interpretatie** — dat hoort in de spec ter discussie.
> Alle configuratiewaarden hieronder zijn uitgelezen van de draaiende machine, niet uit documentatie.

**Doel:** input voor een spec voor een *leeratelier* — een laag over de bestaande POC's waarmee
verschillende doelgroepen (meer) kunnen leren.

Kerncijfers: 12 projecten · 6 publiek bereikbaar · 9 in git · **50+ publieke routes** · 1 machine.

---

## 0. Wat de live pagina's zelf al blootleggen

Twee dingen die uit het ophalen van de publieke sites kwamen en die het ontwerp veranderen:

**Waterlab is al deels een leerplatform.** De landingspagina heeft secties met de titels
`0 · Leerplatform — wat dit laat zien`, `1 · Wat is deze proef?`, `2 · Lessons learned (samenvatting)`,
`Leerpunten`, en `⚠ Bronnen van de synthetische inflow — en waarom ze faalden`. De didactische toon
is er dus al; het atelier hoeft dat niet uit te vinden maar kan het uitbouwen.

**LeefomgevingLab heeft al een datakwaliteit-curriculum.** De pagina `/kwaliteit` heet
"**Kwaliteit per POC**" en behandelt acht POC's, elk met functionele beschrijving, technische
beschrijving, kwaliteitsaspecten **getagd in zes categorieën**, en een follow-up. Plus een
afsluitende sectie "Wat steeds terugkomt". Dat is in feite een kant-en-klare leerlijn datakwaliteit.

De zes kwaliteitscategorieën die daar gehanteerd worden:
`Databron` · `Geo/CRS` · `API-contract` · `Performance` · `Antwoordkwaliteit & veiligheid` · `Onderhoudbaarheid`

En de terugkerende lessen, letterlijk van die pagina:

- **Geo/CRS** — "Coördinaatstelsel is keer op keer de valkuil: RD vs WGS84, asvolgorde, en de
  CRS-notatie (EPSG:28992 vs OGC-URI) verschillen per DSO-deel-API. Altijd live verifiëren met een
  bekend punt."
- **API-contract** — "Gegokte endpoints/headers/veldnamen kloppen zelden; de OpenAPI-spec + een live
  call zijn nodig vóór het bouwen."
- **Databron** — "Veel DSO-bronnen werken alleen op pre-productie en zijn in de oefenomgeving dun
  gevuld → best-effort + nette degradatie i.p.v. harde aannames."
- **Antwoordkwaliteit** — "Een conservatief antwoordcontract (disclaimer, vangnet, geen stellige
  uitspraak) is een harde eis — maar mag niet zó streng zijn dat het nuttige, gevonden informatie
  onderdrukt."
- **Onderhoudbaarheid** — "Elke bron is een aparte connector achter één basis-connector (cache +
  degradatie); een fout in één bron laat de andere nooit vallen."
- **Performance** — "De chatbot-keten is sequentieel en hardware-gebonden (~50-70s bij koude cache);
  parallelliseren is een aparte optimalisatie."
- **Review-status** — "Intern getoetst per feature (test-driven, per-taak code-review, whole-branch
  review per plan); nog geen externe/vakgenoot-review."

---

## 1. POC-inventaris

### LeefomgevingLab — LIVE
`/mnt/nvme/workspaces/LeefomgevingLab` · https://leefomgevinglab.felixisfelix.com · FastAPI :8792

BALO-proeftuin. **18 publieke pagina's, 21 API-endpoints** (uit `/openapi.json`; interne titel is nog
`Geluidsmeter API` v0.1.0 — historische naam).

| Pagina's | API |
|---|---|
| `/` `/afval` `/chatbot` `/dashboard` `/datavraag` `/demo` `/kwaliteit` `/meten` `/poc` `/public` `/roadmap` `/semantiek` `/viewer` `/wfs-kwaliteit` `/health` `/latest` `/metadata` `/summary` | `/api/afval/{meta,choropleth,trend,duiding,forecast,bronnen,chat}` · `/api/chat` · `/api/regels` · `/api/rev/features` · `/api/duiding` · `/api/datavraag` · `/api/ld/sparql` · `/api/semantiek/{graph,node}` · `/api/locations` · `/api/submit` · `/api/wfs-kwaliteit` · `/geodata/{bgt,nwb,rivm}` |

Acht POC's volgens de eigen kwaliteitspagina: geluidsmeter, REV-viewer, semantische browser,
datavraag-chatbot, vergunningen-RAG over IPLO, DSO toepasbare regels, omgevingsplan-regels (Ozon),
externe-veiligheid-waarschuwing. Roadmap noemt als volgende: lucht (UC-07), stelselcatalogus (UC-09),
BRZO/Seveso (UC-12), bron-radar, digital twin-stub, samenhangend objectbeeld (SOR), en eigen data
als OGC API + linked data.

### Waterlab — LIVE
`/mnt/nvme/workspaces/waterlab` (repo `wflow_ijssel`) · https://waterlab.felixisfelix.com · FastAPI :8000

**29 routes.** Naast de dashboards twee architectonisch interessante lagen:

- **FEWS PI-REST-emulatie** — `/fews/rest/fewspiservice/v1/{filters,locations,parameters,timeseries}`.
  Waterlab biedt zichzelf aan als FEWS-service: een bestaand vakinterface nagebouwd zodat bestaande
  clients erop passen.
- **GraphQL-façade** — `/graphql`, "één query-laag over het domein".
- Modellering: `/api/{forecast,ensemble,multimodel,assimilation,assimilation/sandbox,validation,
  validation/hindcast,kpis,timeseries/{station},river/{day},grondwater/*}`, plus jaar-gescopeerde
  varianten `/api/{year}/...`.
- Casussen op de site: hoogwater 1995, droogte 2018, hoogwater juli 2021, BRO grondwater-koppeling.

Stack: hydromt-wflow, xarray, netCDF4, geopandas/pyproj/shapely, FastAPI. Julia-depot 2,1 GB
(`~/.julia`) voor wflow/Ribasim.

### Morele Helper — DRAAIT, publiek stuk kapot
`~/morele-helper` + `~/morele-helper-relay` · admin.helper.felixisfelix.com (**TLS-fout**) · :8788

21 werkdagen dagelijkse audio-reflectie op één beleidsdilemma via reTerminal-knop, twee tekstvragen
terug, eindigend in een narratieve beleidsrapportage op dag 21.
*Leerwaarde:* het enige project met een ingebouwd leertraject — ritme mét eindproduct.

### Derwisch — LIVE
`~/Derwisch_local` + `~/derwisch-relay` · https://felixisfelix.com (via :8790) · backend :8789 (https, self-signed)

Gesproken reflectie → STT → lokale LLM door een gekozen *variant* → reTerminal via Vercel-relay.
Drie promptlagen: variant (identiteit) / dagelijkse lens (interpretatiekader) / transcript (ervaring).
Variant-switch is atomair: één klik wisselt profiel, plan, dagmodules én studio-adviseurs tegelijk.

### De twee relays — LIVE
Vercel + Upstash KV. `POST /api/update`, `GET /api/latest?channel=…`. Eén patroon, twee toepassingen.

### Sysmonitor — LIVE
`~/sysmonitor` · https://status.felixisfelix.com (Basic-Auth) · :8795 · **geen git**
Dagelijkse timer → 14 diensten, 5 endpoints, schijf/geheugen/temp/load/security/verkeer → HTML + JSON
+ history.jsonl (90 dagen). Alleen stdlib. Elke warn/crit krijgt een concrete actie (`advise()`).

### Docuchat — GEREEDSCHAP
`~/docuchat` · docker-compose (rag-api) + `scan_docs.sh` · **geen git**, geen publieke demo.

### Transcribe — GEREEDSCHAP
`~/transcribe` · faster-whisper NL int8, m4a → txt · **geen git**. Voedt Derwisch en Morele Helper.

### Labs-MCP — GEREEDSCHAP
`~/labs-mcp` · geen dienst, geen poort, niet publiek · **git**, Apache-2.0 nog te controleren.
Eén `age`-versleutelde kluis (`~/.config/labs-secrets/`, `chmod 600`, buiten elke git-map) plus
`labsctl` (284 regels, stdlib + `age`): kluis, render naar `EnvironmentFile`/`.auth`, en een audit op
verval en publieke lekken. Daarbovenop `mcp_server.py` (71 regels) die vijf handelingen aanbiedt aan een
AI-assistent: `secret_list`, `secret_get`, `secret_set`, `secret_render`, `secret_audit`.
**Aangesloten: 2 van de 12** — `derwisch-ritueel` (→ `/etc/derwisch/ritueel.env`) en `sysmonitor`
(→ `~/sysmonitor/.auth`). Vast principe: de kluis is beheer-gemak, **geen draaivereiste** — elk project
heeft een gecommitte `.env.example` en draait standalone.
Bekende gebreken: de lekcontrole gaf 403-weigeringen als "in orde" terug (nu met browser-User-Agent) en
sloeg aan op gebruikersnamen (nu overgeslagen). In juli stonden er echte wachtwoorden in een
ontwerpdocument en een testfixture; die zijn geredigeerd maar staan nog in de geschiedenis.

### BluesLab — SLUIMERT
`~/BluesLab` · 12-maats schema + bluestoonladder + akkoordtonen, getransponeerd naar Bes-klarinet en
alt-sax; interne representatie altijd concert pitch. `core/theory.py` is pure stdlib-logica.

### Felix Nazaten — LIVE
`~/felix-nazaten` · https://upload.felixisfelix.com · :8791. Genealogie Felix-Peeters + uploadserver.
Node v12.22.9 — harde beperking waar de code omheen geschreven is.

### Julian Media — SLUIMERT
`~/julian-media` · media + `julian.json`. Kandidaat om buiten scope te laten.

### felixisfelix-site — SLUIMERT
`~/felixisfelix-site` · statische site op Vercel. **Let op:** de apex felixisfelix.com wordt nu door
de Cloudflare-tunnel naar :8790 gestuurd — dubbel belegd.

---

## 2. Technische configuratie

Alles uitgelezen van de draaiende machine op 2026-09-02.

### Hardware & platform
| | |
|---|---|
| Machine | NVIDIA Jetson AGX Orin 64GB, aarch64 |
| GPU | Orin, CUDA compute capability **8.7**, unified memory |
| L4T / JetPack | **R36.4.7** (BOARD generic, EABI aarch64, sept 2025) |
| Kernel | 5.15.148-tegra |
| OS | Ubuntu 22.04.5 LTS · Python 3.10.12 |
| Power mode | **MAXN** (mode 0, ongelimiteerd) |
| RAM | 61 GB totaal, ~30 GB in gebruik, 15 GB swap (bestand `/mnt/16GB.swap`) |
| Opslag | eMMC `/` 57 GB (81% vol) · NVMe `/mnt/nvme` 916 GB (83% vol) |

### AI-runtime — dit is de kern van de AI-architectuur-leerlijn
| | |
|---|---|
| Engine | llama.cpp, build **8117 (b908baf18)**, CUDA-backend |
| Generatief model | **Qwen2.5-32B-Instruct**, Q4_K_M, 5 GGUF-shards, 19 GB op schijf |
| — draait als | `llama-server --host 127.0.0.1 --port 8080 --ctx-size 4096 --n-gpu-layers 99 --threads 4` |
| Embeddings | **bge-m3 FP16**, 1,1 GB |
| — draait als | `llama-server --embeddings --port 8082 --ctx-size 8192 --n-gpu-layers 99 --threads 4` |
| STT | faster-whisper, Nederlands, `device="cpu"`, `compute_type="int8"` |
| Niet actief | mistral-nemo-instruct (7 GB), qwen2.5-coder-14b (8,4 GB), steerling-8b (17 GB) — units disabled |
| Modelpad | `/mnt/nvme/nvme/models/` (dubbel "nvme" — bekende valkuil) |

Twee ontwerpkeuzes die uitleg verdienen in een atelier: **beide servers luisteren op 127.0.0.1**
(alleen lokaal bereikbaar, apps praten er intern mee), en **`--n-gpu-layers 99`** duwt het hele model
naar de GPU — mogelijk doordat Orin unified memory heeft en er dus geen aparte VRAM-limiet is.

### RAG-opstelling
| | |
|---|---|
| Pijplijn | IPLO/DSO-docs → chunking → embeddings via llama.cpp `/v1/embeddings` (:8082) → vectorstore |
| Vectorstore | **`vectors.npy` (33 KB) + `chunks.jsonl` (8,7 KB)** — platte numpy, geen vector-database |
| Locatie | `/mnt/nvme/geluidsmeter/data/rag/` · gebouwd met `scripts/07_build_rag_index.py` |
| Laatst gebouwd | 2026-06-21 |
| Ketenlatency | ~50-70 s bij koude cache (sequentieel, hardware-gebonden) |

De index is dus **zeer klein en drie maanden oud**. Als de vergunningen-chatbot lesmateriaal wordt,
is herbouwen en vergroten een voorwaarde. Tegelijk is "RAG zonder vector-database, gewoon numpy" een
sterk didactisch punt: het ontmythologiseert de stack.

### Data
| | |
|---|---|
| Hoofdmap | `/mnt/nvme/geluidsmeter/data/` (naam historisch, bevat alle LeefomgevingLab-data) |
| Afval | `external/afval/afval.duckdb` — **DuckDB, 2,9 MB**, canoniek datamodel CBS↔AMICE |
| Externe bronnen | `external/{afval,atlas,bgt,cvgg,pdok_3d_geluid,rivm}` — 11 MB |
| Geluid | `raw_features/` 3,4 MB JSONL → `processed/` GeoParquet → `catalog/` STAC (Portolan) |
| Linked data | `ld/` (REV-LD) · `semantiek/` (IMX-Geo/IMEV) |
| Cache | 44 MB |

### Netwerk & publicatie
| | |
|---|---|
| Tunnel | cloudflared, **dashboard-managed** (Zero Trust → Public Hostnames, niet de lokale config.yml) |
| Tunnel-UUID | `ca12e4f6-fa0d-4f39-8868-e729d9369c5c` · 3 verbindingen naar ams07/18/20 |
| Origins | alle op **plain HTTP** naar localhost — TLS eindigt bij Cloudflare |
| Ingress | felixisfelix.com→8790 · upload→8791 · transcribe→8790 · julianfelix→8791 · leefomgevinglab→8792 · admin.helper→8788 · waterlab→8000 · status→8795 |
| Beheertoegang | Tailscale, node `orin3` = 100.112.6.2, MagicDNS `orin3.tail897ef4.ts.net` |
| Extern platform | Vercel (2 relays + site) + Upstash KV |
| Git | 9 repo's, GitHub `bopfelix-derwisch`, remotes sinds 2026-09-02 op **SSH** |

### Poorten
| Poort | Dienst | Bind |
|---|---|---|
| 8000 | waterlab-dashboard (uvicorn) | 0.0.0.0 |
| 8080 | llama-server Qwen2.5-32B | 127.0.0.1 |
| 8082 | llama-server bge-m3 embeddings | 127.0.0.1 |
| 8788 | morele-helper-admin | 0.0.0.0 |
| 8789 | derwisch_local-backend (**https**, self-signed) | 0.0.0.0 |
| 8790 | derwisch-transcribe | 0.0.0.0 |
| 8791 | felix-upload | 0.0.0.0 |
| 8792 | leefomgevinglab-api | 0.0.0.0 |
| 8795 | sysmonitor-web (Basic-Auth) | 127.0.0.1 |
| 8799 | (python, ritueel) | 127.0.0.1 |
| — | 8081 is **leeg**: derwisch_local-nemo is disabled | |

### Diensten (14 bewaakt, alle enabled + active)
`cloudflared` · `tailscaled` · `sysmonitor-web` · `waterlab-dashboard` · `leefomgevinglab-api` ·
`leefomgevinglab-embed` · `derwisch_local-backend` · `derwisch_local-llm` · `derwisch_local-ritueel` ·
`derwisch-transcribe` · `morele-helper-admin` · `morele-helper-button` · `felix-upload` · `prive-tts`
Niet actief: `leefomgevinglab-capture` (C922 gedeeld met Derwisch), `derwisch_local-nemo`.

### Beveiliging & toegang
- Statuspagina: Basic-Auth, `.auth` met **sha256-hash** (nooit platte tekst), wijzigen via `./setpw.sh`.
- Derwisch-backend: HTTPS met self-signed cert op LAN; Studio-PIN in de systemd-unit.
- DSO/API-sleutels in `.env` per project (niet in git).
- `core/location_private.yaml` (echte meetcoördinaten) staat in `.gitignore`; publieke locatie bewust
  **afgerond** gepubliceerd — privacy-by-design als aanwijsbaar voorbeeld.
- Geluidsmeter slaat **geen ruwe audio** op, alleen features (RMS/Lmax/banden).
- passwordless sudo staat aan op de machine.

### Monitoring-drempels (sysmonitor)
schijf 85/95% · geheugen 85/95% · temperatuur 80/90 °C · load 1,5×/3,0× cores · mislukte SSH 20/100 per
24u · logdir 500/1500 MB. Huidige temperaturen: CPU 48 °C, GPU 46 °C.

---

## 3. Leerlijnen

Zes lijnen door hetzelfde materiaal. De eerste vier zijn door jou benoemd; 5 en 6 volgen uit wat er ligt.

### L1 · AI-architectuur
**Voor:** architecten, technisch leiders, opdrachtgevers met een AI-vraag.
**Materiaal:** de volledige lokale stack (llama.cpp + Qwen 32B + bge-m3 + faster-whisper op één
Jetson); het relay-patroon naar Vercel/KV; RAG zonder vector-database; de drielaagse prompt-architectuur
van Derwisch; de FEWS-PI-emulatie en GraphQL-façade van Waterlab als voorbeelden van "pas je aan een
bestaand vakinterface aan" versus "bied een nieuwe query-laag".
**Kernvraag:** wanneer is klein, lokaal en saai het juiste antwoord — en wanneer niet?

### L2 · Datakwaliteit
**Voor:** data-eigenaren, informatiemanagers, bronhouders, DSO/stelselmensen.
**Materiaal:** `/kwaliteit` (acht POC's, zes categorieën, follow-up per punt), `/wfs-kwaliteit`
(datakwaliteit REV-WFS), `/api/wfs-kwaliteit`, en "Wat steeds terugkomt". Concrete casussen:
INSPIRE-laag levert EPSG:4258 met lat,lon-asvolgorde en negeert `bbox-crs`; productiefaciliteiten
verdeeld over zes collections waarvan de eerst gekozen bijna leeg was; ongeldige bbox gaf ongevangen
500 → nu nette 400.
**Kernvraag:** hoe weet je of een bron doet wat de documentatie belooft? Antwoord van dit lab:
OpenAPI-spec + live call met een bekend punt, altijd.

### L3 · Open source & open data beleid
**Voor:** beleidsmakers digitalisering, CIO-office, juristen, bestuurders.
**Materiaal:** publiceren op echte open data (CBS 83558NED CC-BY 4.0, PDOK, RIVM, Kadaster KKG);
rolzuiverheid conform BALO (afnemer, nooit bronhouder/schaduwregister); DSO productie- versus
pre-productie-omgevingen; alles op GitHub.
**Maar ook — en dit is de scherpste les:** **geen enkele repo heeft een LICENSE-bestand.** Zonder
licentie is code juridisch "alle rechten voorbehouden", dus formeel niet open source, hoe publiek de
repo ook staat. Een leerlijn open source beleid die begint met het repareren van je eigen omissie is
geloofwaardiger dan één met een schoon voorbeeld.
**Kernvraag:** wat maakt iets werkelijk herbruikbaar — beschikbaarheid, licentie, of documentatie?

### L4 · Persoonlijk gebruik — HOW TO
**Voor:** individuele professionals, nieuwsgierige beginners, iedereen die het zelf wil.
**Materiaal, opklimmend:** Transcribe (één script, één taak) → Docuchat (kaalste RAG) → BluesLab
(domeinlogica scheiden van weergave, zonder domeinruis) → Derwisch (je eigen coachingsritueel
inrichten) → een eigen POC in het patroon "bron → bewerking → visualisatie → duiding met bronverwijzing".
**Kernvraag:** wat kan ik vanavond op mijn eigen machine draaien, en wat heb ik daar echt voor nodig?

### L5 · Domeininhoud
**Voor:** waterbeheerders, omgevingsdienst-medewerkers, vakspecialisten.
**Materiaal:** Waterlab (wflow SBM, Ribasim, ensembles, assimilatie, hindcast-validatie, casussen
1995/2018/2021) en LeefomgevingLab (afval/circulariteit, externe veiligheid, vergunningen, geluid, lucht).
**Kernvraag:** wat zegt dit model wél en niet, en waar komt vertrouwen vandaan?

### L6 · Reflectie & oordeelsvorming
**Voor:** ambtenaren, leidinggevenden, professionals met dilemma's.
**Materiaal:** Morele Helper (21 werkdagen, eindigend in een beleidsrapportage) en Derwisch
(persoonlijk ritueel). AI als spiegel, niet als antwoordmachine.
**Kernvraag:** waar helpt een taalmodel je denken, en waar neemt het je denken over?

---

## 4. Doelgroepen × leerlijnen

| Doelgroep | Primair | Secundair |
|---|---|---|
| Architecten / technisch leiders | L1 AI-architectuur | L2, L3 |
| Datakwaliteit- & stelselmensen | L2 Datakwaliteit | L3, L5 |
| Beleid open source / open data | L3 Beleid | L2, L1 |
| Individuele professionals | L4 How-to | L6 |
| Vakmensen water / leefomgeving | L5 Domein | L2 |
| Ambtenaren met dilemma's | L6 Reflectie | L4 |
| Bestuurders / opdrachtgevers | L1 + L3 | kostenkant, sysmonitor |

---

## 5. Wat de spec nog moet beslissen

**Vraag 1, 4 en 7 zijn de scharnieren** (vorm, eerste doelgroep, schaal); de rest volgt.

**Vorm en belofte**
1. Wat ís een leeratelier hier — fysiek, digitaal of hybride?
2. Wat is het product: curriculum, reeks workshops, website, of begeleid traject?
3. Wat moet een deelnemer na afloop kunnen of anders doen?

**Deelnemers**
4. Welke doelgroep en welke leerlijn zijn de eerste? (Zeven doelgroepen × zes leerlijnen tegelijk
   bedienen levert een atelier voor niemand op.)
5. Rol van de deelnemer: kijken, meedoen in de demo's, of zelf bouwen?
6. Leren ze over AI en data mét de POC's als voorbeeld, of over het domein mét AI als middel?

**Praktijk en grenzen**
7. Hoeveel mensen tegelijk, en publiek of besloten? (Eén Jetson, één 32B-model op ctx 4096, één
   tunnel, chatbot-latency 50-70 s bij koude cache. Een klas van twintig die tegelijk bevraagt is een
   capaciteitsvraag, geen detail.)
8. Wat mag er met persoonlijke invoer gebeuren? (AVG — reflectie-audio, geluidsopnames.)
9. Hoe bewaak je de disclaimer als er lesgegeven wordt?
10. Wie kan het draaien — alleen jij, of moet een ander het kunnen overnemen?

**Techniek**
11. Aparte laag naast de POC's, of ingrijpen in de bestaande repo's?
12. Welk ritme: eenmalige sessie of traject over meerdere dagen? (Morele Helper heeft al een werkend
    21-dagenmodel.)

**Nieuw, uit de configuratie-inventarisatie**
13. **Krijgen de repo's een licentie, en zo ja welke?** Blokkeert leerlijn L3 zolang het niet geregeld is.
14. **Wordt de RAG-index herbouwd en vergroot?** Nu 33 KB vectoren uit juni; te dun voor lesgebruik.
15. **Wat gebeurt er met de niet-gebruikte modellen?** 32 GB aan Nemo, coder-14b en steerling-8b staat
    stil op **NVMe** (83% vol, 155 GB vrij) — dus niet urgent, en het **helpt niet** tegen de krappe
    rootschijf, want die staat op eMMC. Opruimen, of bewust bewaren als vergelijkingsmateriaal in L1?

---

## 6. Losse einden die het atelier raken

- **admin.helper.felixisfelix.com geeft een TLS-fout.** Cloudflare Universal SSL dekt
  `*.felixisfelix.com` maar niet het vierde niveau. Dienst draait (lokaal 8788 → 401), maar het
  dashboard van het meest didactische project is publiek onbereikbaar. Fix: custom cert of hernoemen
  naar `helper-admin.felixisfelix.com`.
- **Geen enkele repo heeft een LICENSE-bestand.** Zie L3.
- **docuchat, transcribe en sysmonitor zitten niet in git.**
- **felixisfelix.com is dubbel belegd** tussen de statische Vercel-site en de Cloudflare-tunnel.
- **De interne API-titel van LeefomgevingLab is nog `Geluidsmeter API`** — zichtbaar in `/openapi.json`
  en dus in elke gegenereerde client. Cosmetisch, maar zichtbaar voor deelnemers.
- **`/` staat op 81% (11 GB vrij).** Bij lesgebruik met meerdere deelnemers is dat krap. Let op: de
  modellen staan op NVMe, dus die opruimen geeft hier géén ruimte. Grootste posten in `~`: `.local`
  3 GB, `.cache` 2 GB, `.julia` 2,1 GB.
