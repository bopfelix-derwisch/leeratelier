# Klasmodel permanent op :8081 — WP-04 — 2026-09-03

Het klasmodel uit WP-03 (`Qwen3-8B` Q4_K_M) draait als systemd-unit `llama-klasmodel.service`, enabled,
active, met `Restart=always` en `StartLimitIntervalSec=0`.

**De belangrijkste uitkomst van dit werkpakket is niet de unit maar de toets die eraan voorafging:
vondst V1 uit WP-01 was fout, en zonder die toets was er een unit met 1024 tokens per slot in productie
gegaan.**

---

## 1. De toets die V1 omkeerde

WP-01 concludeerde dat `--ctx-size` op deze build per slot werkt in plaats van als totaal, en `CLAUDE.md`
is daarop aangepast. Die conclusie kwam uit één waarneming: het draaiende showmodel geeft `--ctx-size 4096`
mee zonder `--parallel`, en `/props` meldt dan vier slots van elk 4096.

De backlog schreef voor die aanname te toetsen met een verse server voordat de unit wordt vastgezet. Drie
varianten, hetzelfde model, build 8117:

| vlaggen | `n_ctx` (totaal) | `n_ctx_seq` | slots × per slot |
|---|---:|---:|---|
| `--ctx-size 4096` (geen `--parallel`) | 4096 | 4096 | 4 × 4096 |
| `--ctx-size 4096 --parallel 4` | 4096 | **1024** | 4 × **1024** |
| `--ctx-size 16384 --parallel 4` | 16384 | 4096 | 4 × 4096 |

**Zodra `--parallel` expliciet staat, is `--ctx-size` het totaal en wordt het gedeeld.** De oorspronkelijke
regel in `CLAUDE.md` had dus gelijk voor precies het geval dat deze unit gebruikt. Mijn correctie in WP-01
generaliseerde één waarneming in de auto-modus te breed.

De unit stond na WP-03 op `--ctx-size 4096 --parallel 4` — vier slots van 1024 tokens. Dat is te weinig
voor een module met RAG-context erbij; een bezoeker zou halverwege een afgekapt gesprek hebben gekregen.
Nu: `--ctx-size 16384 --parallel 4`.

## 2. De unit

```ini
ExecStart=/usr/local/bin/llama-server \
  --model /mnt/nvme/nvme/models/qwen3-8b/Qwen3-8B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8081 \
  --ctx-size 16384 --parallel 4 \
  --reasoning-budget 0 \
  --n-gpu-layers 99 --threads 4
Restart=always
RestartSec=10
StartLimitIntervalSec=0
```

`--reasoning-budget 0` is niet optioneel (vondst V7). Geverifieerd na de start met een echte vraag: geen
`<think>`-blok in het antwoord.

## 3. Geheugen

| | |
|---|---:|
| `free -m` vóór de start | 35 894 MB in gebruik |
| `free -m` ná de start | 36 286 MB in gebruik |
| **werkelijk beslag van het proces** (`VmRSS`) | **7,58 GB** |
| model op de GPU (`CUDA0 model buffer`) | 4 455 MiB |
| compute buffer | 305 MiB |

Het verschil in `free` (+392 MB) is misleidend: het model is mmap'd en de pagina's stonden al in
page-cache van de ijkset-runs. `VmRSS` van het proces is de eerlijke maat.

**Blijft er ruimte over voor het showmodel?** Ja. Met klasmodel, showmodel en embeddings samen draaiend
staat de machine op ongeveer 36 GB van 62,8 GB. Er is nog ruim 25 GB vrij — genoeg om het showmodel later
te vervangen door het 18,4 GB MoE-model (besluit B16, variant A) zonder in de knel te komen die vondst V4
beschrijft.

## 4. Gelijktijdigheid gemeten

`config/budget.yaml` had `gelijktijdig.klasmodel: 4` staan als gok, met de aantekening dat het in WP-04
getoetst moest worden.

| gelijktijdig | p50 | p95 | ttft | tok/s per stroom | doorzet |
|---:|---:|---:|---:|---:|---:|
| 1 | 5,50 s | 5,71 s | 0,07 s | 24,31 | 10,9 /min |
| 2 | 5,87 s | 5,90 s | 0,13 s | 22,63 | 20,5 /min |
| 4 | 9,75 s | 10,16 s | 0,25 s | 13,81 | 24,4 /min |
| 8 | 17,76 s | 18,89 s | 4,52 s | 10,63 | 25,4 /min |

De knik ligt bij 2 — daar verdubbelt de doorzet vrijwel voor 0,4 s extra. Maar bij 4 is p95 nog altijd
maar 10 s, ruim onder de warn-drempel van 60 s uit plan §8, en dat levert nog eens 19% doorzet.
**De gok van 4 blijkt juist en blijft staan**, nu als meting.

Bij 8 springt de tijd tot het eerste teken naar 4,5 s voor slechts 4% extra doorzet. Daar niet heen.

## 5. Wat dit voor het dagbudget betekent

Het budget van 300 beurten is in WP-01 afgeleid uit het **showmodel** (4,3 antwoorden/min bij de knik).
Sinds dit werkpakket beantwoordt het **klasmodel** de bezoekersvragen, en dat haalt 20,5 antwoorden/min
bij dezelfde knik — bijna vijf keer zoveel. Dezelfde afleiding zou nu op ongeveer 1800 uitkomen.

**300 blijft staan.** Het is daarmee ongeveer twee procent van het theoretische plafond, en dat is bewust:
verhogen kan met één regel zodra er echte bezoekers zijn, een slechte eerste ervaring terugdraaien niet.
Genoteerd in `config/budget.yaml` onder `herkomst.ruimte_na_wp04`.

## 6. Wat niet getoetst is

De backlog vraagt of de unit **een reboot overleeft**. Dat is niet getest: een reboot van `orin3` legt
Derwisch, LeefomgevingLab, waterlab, de relays en sysmonitor tegelijk plat, en dat is geen beslissing van
een werkpakket. `systemctl is-enabled` geeft `enabled` en het symlink in `multi-user.target.wants/` staat
er, dus de unit start mee — maar dat is een redenering, geen waarneming. **Toets dit bij de eerstvolgende
geplande herstart** en vink het dan pas echt af.

## 7. Verificatie

```
$ systemctl is-enabled llama-klasmodel && systemctl is-active llama-klasmodel
enabled
active

$ curl -s http://127.0.0.1:8081/v1/models
{"models":[{"name":"Qwen3-8B-Q4_K_M.gguf", ... }]}

$ curl -s http://127.0.0.1:8081/slots | ...
slots: 4   n_ctx per slot: [4096, 4096, 4096, 4096]

$ for p in 8080 8081 8082; do curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:$p/health; done
200
200
200
```

## 8. Wat hier misging

Twee dingen, en ze horen allebei in module K6 over draaiend houden.

**De unit was al ingevuld voordat de aanname getoetst was.** In WP-03 heb ik model, pad en
`--reasoning-budget 0` in `ops/systemd/llama-klasmodel.service` gezet, inclusief `--ctx-size 4096
--parallel 4` op basis van mijn eigen foute V1. Dat voelde als vooruitwerken; het was een fout die alleen
niet doorwerkte omdat de backlog een toets voorschreef. De les is niet "toets meer" maar: **een
configuratie die op één waarneming rust, is een aanname met een getal erin.**

**Een steekproef van één vraag legde een probleem bloot dat honderd antwoorden hadden verborgen.** Na het
starten van de unit stelde ik één controlevraag — "Wat is Lden?" — en het antwoord was fout. Dat leidde
naar ijk-05 in de ijkset, waar álle vijf de modellen falen en twee ervan Lden in het domein luchtvervuiling
plaatsen. Dat stond al in de data van WP-03; ik had het niet gelezen omdat ik op ijk-20, ijk-13 en ijk-12
gefocust was. Zie vondst V8 en de nagekomen sectie 4b in `ops/ijking/ijkset-rapport-2026-09-02.md`.
