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

## Nog te vullen door metingen

| Bron | Vraag | Status |
|---|---|---|
| WP-01 | Wat is het werkelijke dagbudget? | **gemeten 2026-09-02** — 300 beurten/dag, afgeleid vanaf de knik bij gelijktijdigheid 2 (4,3 antw./min). Zie `ops/ijking/rapport-2026-09-02.md`. Of je op 300 of op de helft begint is open vraag 4. |
| WP-02 | Werkt MoE op deze build (SM87, issue 19219)? | open — bepaalt of Gemma 4 26B-A4B kan |
| WP-03 | Welk model wordt klasmodel? | open — advies: dense Qwen in de 8B-klasse |
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
| V2 | **`steerling-8b` staat met 17 GB op schijf** — dat is FP16, geen Q4. | 2026-09-02 | Als kandidaat-klasmodel te zwaar naast het 19 GB-showmodel. Meenemen in **WP-03**; een Q4_K_M-variant is ~5 GB. |
| V3 | **De modelaanroep is sneller dan de keten** — 24 s bij rust tegen de 50-70 s die het plan noemt. Het verschil zit in de RAG-stap. | 2026-09-02 | De ketenlatency uit het plan blijft staan, maar de oorzaak ligt niet bij het model alleen. Relevant voor **WP-09b** en module K3. |
