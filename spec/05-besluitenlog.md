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

## Nog te vullen door metingen

| Bron | Vraag | Status |
|---|---|---|
| WP-01 | Wat is het werkelijke dagbudget? | open — `config/budget.yaml` bevat een **schatting** |
| WP-02 | Werkt MoE op deze build (SM87, issue 19219)? | open — bepaalt of Gemma 4 26B-A4B kan |
| WP-03 | Welk model wordt klasmodel? | open — advies: dense Qwen in de 8B-klasse |
| WP-09a | Hoeveel fragmenten zitten er in de RAG-index? | **bevestigd: 8** — `vectors.npy` heeft shape (8, 1024) dtype `<f4`, `chunks.jsonl` telt 8 regels (gelezen 2026-09-02). Het volledige WP-09a-rapport (bronnen, bouwdatum, tekstlengte) moet nog. |

## Openstaand risico

**Bus factor 1.** "Iedereen met login" beantwoordt wie het mag *gebruiken*, niet wie het kan *beheren*.
Bij permanent bedrijf blijft een storing om 22:00 staan tot de beheerder wakker is. Kies één van twee:
een tweede persoon met sudo en Tailscale, of de verwachting expliciet verlagen op de inlogpagina.
Allebei overslaan is het risico. Zie WP-18.
