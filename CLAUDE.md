# CLAUDE.md — werkinstructies voor dit project

> **Machine-breed:** `~/.claude/CLAUDE.md` + `/home/bob/ORIN3_SYSTEEM.md` — daar staan de infra-feiten
> die alle projecten delen; niet hier herhalen.
> **Domein:** dwarsdoorsnede — een leerlaag óver de POC's heen, geen eigen POC.
> **Start via** `orin3` → window **`0:leeratelier`** (canoniek pad `/mnt/nvme/workspaces/leeratelier`;
> `~/leeratelier` is een symlink daarheen).
> **Inventaris:** `docs/inventaris-orin3.md` — de geverifieerde inventaris van alle twaalf projecten.
> Let op: de zes leerlijnen L1–L6 in §3 daarvan zijn **achterhaald** door de route in
> `spec/plan-v0.3.md` §6 (basisroute K1–K7 + spoor W + spoor L). Gebruik de inventaris als feitenbron,
> niet als indeling.

## Wat dit is

Het **Leeratelier** is een dunne laag naast twaalf bestaande POC's op de machine `orin3`. Bezoekers
loggen in, lopen een route van modules door, stellen vragen aan lokale taalmodellen, en gaan weg met een
ingevulde **beheerkaart** voor hun eigen toepassing.

Doelgroep: **functioneel beheerders en technisch geïnteresseerden**. Zij bouwen niets. Ze gebruiken de
POC's om te begrijpen wat er onder de motorkap gebeurt en wanneer een AI-antwoord niet deugt.

`spec/plan-v0.3.md` is het leidende document. Lees het voordat je aan een werkpakket begint.
`spec/06-backlog.md` bevat de werkpakketten in volgorde.

---

## Absolute grenzen

Deze regels gelden altijd, ook als een taak erom lijkt te vragen.

1. **Raak de bestaande POC-repo's niet aan**, behalve bij WP-00 (fundament). De POC's draaien publiek;
   een fout daar is meteen zichtbaar voor bezoekers.
2. **Nieuwe diensten binden op `127.0.0.1`**, nooit op `0.0.0.0`. De Cloudflare-tunnel praat lokaal met
   de dienst. Dit volgt het patroon van `sysmonitor` (:8795), niet dat van de oudere POC's.
3. **Download nooit modellen of grote bestanden naar `/`.** Die schijf zit op 82% (≈11 GB vrij). Alles
   groot gaat naar `/mnt/nvme/`.
4. **Geen geheimen in git.** Sleutels in `.env` per project; `.env` staat in `.gitignore`. Controleer vóór
   elke eerste commit van een nieuwe repo.
5. **Voeg geen zware afhankelijkheden toe.** Stdlib waar het kan, FastAPI + Jinja2 waar het moet. Geen
   frontend-framework, geen vectordatabase, geen ORM, geen Docker voor de atelierlaag zelf.
6. **Schrijf geen code die een draaiende dienst herstart** zonder dat expliciet in het werkpakket staat.

---

## De machine

Uitgelezen op 2026-09-02 en opnieuw geverifieerd bij het inrichten van deze repo. Als iets hiervan niet
meer klopt: corrigeer het in dit bestand en noteer het in `spec/05-besluitenlog.md`.

| | |
|---|---|
| Hardware | NVIDIA Jetson AGX Orin 64GB, **aarch64**, compute capability 8.7 (Ampere, geen FP8) |
| OS / Python | Ubuntu 22.04.5 LTS · **Python 3.10.12** — geen 3.11+ syntax |
| Geheugen | 61 GB unified (GPU en CPU delen dezelfde pool), ~30 GB in gebruik |
| Schijf | `/` 57 GB op **82%** (11 GB vrij) · `/mnt/nvme` 916 GB op 83% (~155 GB vrij) |
| Inferentie | llama.cpp build **8117 (b908baf18)**, CUDA-backend — geverifieerd via `llama-server --version` |
| Bandbreedte | ~200 GB/s → tokengeneratie is **bandbreedte-gebonden**, niet rekenkracht-gebonden |

### Poorten

| Poort | Status |
|---|---|
| 8000, 8788, 8789, 8790, 8791, 8792, 8795, 8799 | **bezet** door bestaande diensten |
| 8080 | llama-server showmodel (Qwen2.5-32B Q4_K_M, 19 GB), `127.0.0.1` |
| 8081 | **leeg** — hier komt het klasmodel (`derwisch_local-nemo` is disabled) |
| 8082 | llama-server embeddings (bge-m3 FP16), `127.0.0.1` |
| **8793** | **vrij** — atelier-portaal |
| **8794** | **vrij** — leerbemiddelaar |

### Paden

| | |
|---|---|
| Modellen | `/mnt/nvme/nvme/models/` — let op het **dubbele `nvme`**. Per model een submap (`qwen2.5-32b`, `bge-m3`, `mistral-nemo-instruct`, `qwen2.5-coder-14b`, `steerling-8b`); de `.gguf` ligt dus niet los in `models/` |
| RAG-index | `/mnt/nvme/geluidsmeter/data/rag/` (`vectors.npy`, `chunks.jsonl`) |
| Data LeefomgevingLab | `/mnt/nvme/geluidsmeter/data/` — naam is historisch |
| Atelier-database | `/mnt/nvme/leeratelier/atelier.db` — **niet op `/`** |
| Tunnel | cloudflared, dashboard-managed (Zero Trust → Public Hostnames), niet `config.yml` |

---

## Valkuilen die deze machine specifiek heeft

Lees deze vóór je met modellen of de index werkt.

1. **`--ctx-size` gedraagt zich op deze build per slot, niet als totaal.** Oorspronkelijk stond hier
   dat llama.cpp `--ctx-size` over `--parallel` verdeelt. Waargenomen op build 8117 (2026-09-02):
   `derwisch_local-llm` geeft `--ctx-size 4096` mee en zet `--parallel` niet, waarna `/props` meldt
   `total_slots: 4` met per slot `n_ctx: 4096`. `--parallel` staat standaard op `-1` (auto).
   **Toets dit bij WP-04** met een verse server op :8081 voordat je de unit vastzet — de oude regel
   laat je vier keer te veel context aanvragen. Zie `spec/05-besluitenlog.md` vondst V1.
2. **MoE-modellen hangen mogelijk op deze chip.** Bekende llama.cpp-bug op SM87 voor builds ná b7309
   (dec 2025): het model laadt, decode produceert nooit tokens. Zie `ggml-org/llama.cpp` issue #19219.
   Deze machine draait build 8117. **Verifieer dit (WP-02) voordat je op een MoE-model plant.**
3. **De RAG-index is vermoedelijk piepklein.** `vectors.npy` is 33 KB; bij bge-m3 (1024 dimensies) komt
   dat neer op ongeveer 8 chunks fp32. Inspecteer vóór je iets herbouwt (WP-09).
4. **Het modelpad bevat `nvme/nvme`.** Bekende bron van verwarring.
5. **`/` loopt vol.** Elke download, cache of log die per ongeluk op `/` landt, is een probleem.
6. **De interne API-titel van LeefomgevingLab is nog `Geluidsmeter API`.** Zichtbaar in `/openapi.json`.
   WP-00 repareert dat.

---

## Stack en stijl

- **Python 3.10**, FastAPI, Jinja2, server-rendered HTML. Geen JavaScript-framework; alleen kleine
  inline scripts waar het echt niet anders kan (polling van een taakstatus).
- **sqlite3 uit de stdlib** voor budget, logboek en meldingen. Geen aparte databaseserver.
- Zo min mogelijk afhankelijkheden. Het atelier moet zelf een voorbeeld zijn van "klein, lokaal en saai".
- **Taal:** alle tekst die een bezoeker ziet is **Nederlands**. Code, functienamen, variabelen en
  commit-berichten zijn **Engels**. Bestandsnamen van content zijn Nederlands, van code Engels.
- Geen emoji in code of UI. De bestaande projecten gebruiken ze spaarzaam; volg dat.
- Foutafhandeling volgt het patroon van de POC's: **nette degradatie boven harde aannames**. Een
  wegvallend model mag nooit een pagina slopen.

---

## Werkwijze

1. Pak **één werkpakket tegelijk** uit `spec/06-backlog.md`, van boven naar beneden.
2. Lees de relevante paragraaf uit `spec/plan-v0.3.md` voordat je begint.
3. Bouw het, draai het verificatiecommando dat bij het werkpakket staat.
4. Vink het werkpakket af in de backlog en noteer afwijkingen in `spec/05-besluitenlog.md`.
5. Wijkt de werkelijkheid af van dit bestand? Werk `CLAUDE.md` bij. Dit bestand is de bron van waarheid
   over de machine.

**Begin met WP-01, WP-02 en de inspectiehelft van WP-09.** Die drie bepalen hoeveel het atelier aankan,
welk model past, en of de chatbot inhoudelijk sterk genoeg is om lesmateriaal te zijn. Alles daarna hangt
van die uitkomsten af. Bouw geen portaal voordat die metingen er liggen.

---

## Wat je niet moet doen

- Geen portaal bouwen vóór fase 2. Een leeg portaal is de klassieke manier om drie maanden te verliezen.
- Geen modules schrijven voordat het modulecontract (`spec/04-modulecontract.md`) staat.
- Geen budgetwaarden hardcoderen. Ze staan in `config/budget.yaml` en worden na WP-01 bijgesteld.
- Geen aannames over modelgedrag zonder meting. De ijkset (`ops/ijkset-nl.jsonl`) is er om te meten.
- Geen `localStorage` of browseropslag in de UI; alles wat bewaard moet blijven gaat naar sqlite.

---

## Conventies van orin3 die hier ook gelden

- Commits eindigen met de trailer `Co-Authored-By: Claude <model> <noreply@anthropic.com>`, waarbij
  `<model>` het model is dat de commit maakte. **Alleen committen of pushen als erom gevraagd wordt.**
- GitHub-remote: account `bopfelix-derwisch`, remotes op **SSH**, nooit een token in een remote-URL.
  De remote voor deze repo bestaat nog niet — zie `README.md`.
- `find ~` bevriest op deze machine. Gebruik `ls` of specifieke paden.
- Passwordless sudo staat aan. Een nieuwe map direct onder `/mnt/nvme/workspaces/` vraagt wel
  `sudo mkdir … && sudo chown bob:bob …`; de parent is van `marc`.
