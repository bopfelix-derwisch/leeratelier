# Besluitenlog

Alles wat afwijkt van `plan-v0.3.md` komt hier. Ook uitkomsten van metingen die een aanname vervangen.

## Vastgesteld

| # | Besluit | Datum | Motivatie |
|---|---|---|---|
| B1 | Doelgroep is **functioneel beheerders en technisch geinteresseerden** | 2026-09-02 | zij leven met AI-systemen; architecten beslissen erover. Hier valt het meest te winnen. |
| B2 | Interactieniveau 1: **alleen gebruiken, niet bouwen** | 2026-09-02 | browser-only bereikt de doelgroep die anders afhaakt op installatieverboden |
| B3 | **Permanent open**, alles onder inlog | 2026-09-02 | gevolg: onbewaakt bedrijf, conserven als volwaardig pad |
| B4 | Eindproduct is de **beheerkaart**, niet een architectuurnotitie | 2026-09-02 | past bij het dagelijks werk van de doelgroep |
| B5 | Verplichte competenties **B2, B3 en de beheerkaart** | 2026-09-02 | drie is te bewijzen binnen de looptijd, zes niet |
| B6 | **Raamwerk eerst** (dun en compleet), dan één module volledig, dan incrementeel | 2026-09-02 | wandelend skelet; modules kunnen daarna instromen |
| B7 | Aparte repo; POC's blijven ongemoeid behalve WP-00 | 2026-09-02 | een kapotte les mag nooit een draaiende demo slopen |
| B8 | Licentie: **nog te kiezen** — Apache-2.0 of EUPL-1.2 | open | blokkeert geloofwaardig onderwijs over houdbaarheid |
| B9 | Klasmodel apart van showmodel | 2026-09-02 | capaciteit en vergelijkingsmateriaal in één |
| B10 | **Mislukking is doorlopend materiaal**: vaste sectie per module | 2026-09-02 | het waardevolste bezit voor deze doelgroep |
| B11 | Waterlab krijgt een **eigen spoor**, net als LeefomgevingLab | 2026-09-02 | eigen doelgroep; FEWS-emulatie is het interessantste patroon op de machine |
| B12 | **Vragen worden gelogd**, 90 dagen, doel op de inlogpagina | 2026-09-02 | conserven verbeteren en zien waar mensen vastlopen |
| B13 | **Maandelijkse begeleide tegenspraaksessie** | 2026-09-02 | enige schakel tussen route en praktijk |
| B14 | **`gelijktijdig.showmodel` van 1 naar 2** | 2026-09-02 | gemeten: +65% doorzet voor +4 s p95. Van 4 naar 8 kost 38 s extra p95 voor 10% doorzet en 19 s tot het eerste teken — daar niet heen. |
| B15 | **Dagbudget 300, per bezoeker 20** | 2026-09-02 | vervangt de berekende 150/15. Afleiding in `ops/ijking/rapport-2026-09-02.md` §3. Het advies van `meet.py` zelf (3225) is onbruikbaar: het neemt 24 uur volle belasting aan op een gedeelde machine. |
| B16 | **MoE werkt; dense-versus-MoE valt uit op MoE** | 2026-09-02 | Gemeten: 35,1 tok/s tegen 6,5 voor het dense showmodel, bij vrijwel gelijke bestandsgrootte (18,4 vs 19,0 GB). Advies is **variant A**: MoE vervangt het showmodel, klasmodel wordt een klein dens 8B-model. Dat raakt de opzet van B9 niet, wel de invulling. Uitvoering is werk voor WP-03/WP-04; `config/modellen.yaml` staat daarom nog op Qwen2.5-32B. Zie `ops/ijking/moe-verificatie-2026-09-02.md` §6. **Aantekening na WP-03:** de MoE antwoordt STELLIG op ijk-20 en verzint details. Als *showmodel* (demonstratie) is dat acceptabel en zelfs bruikbaar lesmateriaal; als klasmodel zou het diskwalificeren. Voorwaarde is dus dat het klasmodel de eerlijke is — geregeld met B17. |
| B17 | **Klasmodel wordt `Qwen3-8B` Q4_K_M (5,0 GB)** | 2026-09-02 | Gekozen op de ijkset van 20 Nederlandse vragen, 5 modellen, 100/100 antwoorden. Doorslaggevend: het enige model dat op ijk-20 eerlijk is over herkomst en peildatum. Verder correct op ijk-13 waar Nemo en het 4B-model falen, gemiddeld 527 tekens (tegen 1000 voor het 4B-model), 24,1 tok/s. Bevestigt het advies uit plan §5.4, maar nu op meting. Zie `ops/ijking/ijkset-rapport-2026-09-02.md`. |

## Nog te vullen door metingen

| Bron | Vraag | Status |
|---|---|---|
| WP-01 | Wat is het werkelijke dagbudget? | **gemeten 2026-09-02** — 300 beurten/dag, afgeleid vanaf de knik bij gelijktijdigheid 2 (4,3 antw./min). Zie `ops/ijking/rapport-2026-09-02.md`. Of je op 300 of op de helft begint is open vraag 4. |
| WP-02 | Werkt MoE op deze build (SM87, issue 19219)? | **JA, gemeten 2026-09-02** — Qwen3-30B-A3B Q4_K_M decodeert normaal op build 8117, en is 5,4x sneller dan het dense showmodel. Bewijs: `ops/ijking/moe-verificatie-2026-09-02.md`. |
| WP-03 | Welk model wordt klasmodel? | **beantwoord 2026-09-02: `Qwen3-8B` Q4_K_M** — enige van vijf modellen dat eerlijk is over de eigen herkomst (ijk-20), correct op de valstrikken, bondig en 4x sneller dan het showmodel. Zie `ops/ijking/ijkset-rapport-2026-09-02.md`. |
| WP-09a | Hoeveel fragmenten zitten er in de RAG-index? | **bevestigd: 8** — `vectors.npy` heeft shape (8, 1024) dtype `<f4`, `chunks.jsonl` telt 8 regels (gelezen 2026-09-02). Het volledige WP-09a-rapport (bronnen, bouwdatum, tekstlengte) moet nog. |

## Openstaand risico

**Bus factor 1.** "Iedereen met login" beantwoordt wie het mag *gebruiken*, niet wie het kan *beheren*.
Bij permanent bedrijf blijft een storing om 22:00 staan tot de beheerder wakker is. Kies één van twee:
een tweede persoon met sudo en Tailscale, of de verwachting expliciet verlagen op de inlogpagina.
Allebei overslaan is het risico. Zie WP-18.

## Vondsten die documentatie tegenspreken

| # | Vondst | Datum | Gevolg |
|---|---|---|---|
| V1 | **`--ctx-size` werkt per slot, niet als totaal** — op build 8117 geeft `--ctx-size 4096` zonder `--parallel` vier slots van elk 4096 (`/props`: `total_slots: 4`). `--parallel` staat standaard op `-1` (auto). | 2026-09-02 | Valkuil 1 in `CLAUDE.md` beschrijft het omgekeerde. Wie die regel volgt bij **WP-04** vraagt 4x te veel context aan. Toets het daar expliciet met een verse `llama-server` op :8081 voordat de unit vastgezet wordt. |
| V2 | **`steerling-8b` is geen kandidaat-klasmodel** — het is geen GGUF maar safetensors (4 shards, 16,8 GB), en `config.json` meldt `model_type: causal_diffusion`: een masked-diffusion model met een eigen `steerling`-runtime, niet autoregressief. De modelkaart geeft `language: en`. | 2026-09-02 | llama.cpp kan dit niet serveren (geen treffer op `causal_diffusion` in de binary) en Engels-only diskwalificeert het sowieso voor een Nederlandstalig atelier. **Schrap het als optie in WP-03.** Eerdere lezing ("FP16, te zwaar") was op alleen de bestandsgrootte gebaseerd en klopte niet. |
| V3 | **De modelaanroep is sneller dan de keten** — 24 s bij rust tegen de 50-70 s die het plan noemt. Het verschil zit in de RAG-stap. | 2026-09-02 | De ketenlatency uit het plan blijft staan, maar de oorzaak ligt niet bij het model alleen. Relevant voor **WP-09b** en module K3. |
| V4 | **Twee modellen van ~19 GB passen niet naast elkaar.** Het laden van de MoE naast het showmodel faalde twee keer op `cudaMalloc failed: out of memory` / `NvMapMemAllocInternalTagged: error 12`, terwijl `free` 29,8 GB "available" meldde: 18 GB daarvan zat in page-cache, en **NvMap kan page-cache niet opeisen**. Na `drop_caches` laadde het wel, met beide modellen op 47,2 GB gebruikt en 499 MB vrij. | 2026-09-02 | Coëxistentie is aangetoond maar heeft geen werkbare marge voor **onbewaakt** bedrijf. Er moet gekozen worden tussen showmodel en MoE — zie B16. Ook relevant voor de modellenbank in K3: vijf modellen tegelijk draaien kan sowieso niet, conserven zijn daar geen noodgreep maar noodzaak. |
| V5 | **De JetPack-fout achter issue 19219 zit nog op deze machine.** L4T R36.4.7 (GCID 42132812) is exact de versie van de melder; NVIDIA's fix zit pas in een volgende JetPack-release. Onze build 8117 is veilig omdat de trigger (`CUDA_SCALE_LAUNCH_QUEUES`) door PR #19227 verwijderd is. | 2026-09-02 | **Staand risico bij elke llama.cpp-upgrade.** Controleer na een upgrade met `strings $(command -v llama-server) | grep CUDA_SCALE_LAUNCH_QUEUES`; een treffer betekent dat MoE opnieuw hangt tot JetPack bijgewerkt is. |
| V6 | **Op ijk-12 (asvolgorde) faalt élk model** — vijf modellen van 2,5 tot 19 GB geven alle vijf een plausibel en fout antwoord, elk op een andere manier. Het correcte antwoord (asvolgorde volgt uit de CRS-definitie, niet uit de service) komt bij geen van hen boven. | 2026-09-02 | Het veld `let_op` voorspelde dit. Dit is het beste bewijsmateriaal dat de ijkset heeft opgeleverd: het argument "een groter model weet het wel" sneuvelt hier zichtbaar. Bewaren als conserf en naast elkaar tonen in **K4** (faalvorm plausibel-maar-fout) en **K5** (asvolgorde). |
| V7 | **Qwen3-8B is een hybride redeneermodel** en lekt `<think>`-blokken zonder `--reasoning-budget 0`. | 2026-09-02 | Die vlag moet in de systemd-unit van **WP-04**, anders krijgt elke bezoeker het redeneerblok te zien en kost elk antwoord een veelvoud aan tokens. |
