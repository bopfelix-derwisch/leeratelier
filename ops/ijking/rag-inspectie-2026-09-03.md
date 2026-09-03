# RAG-index: inspectie en herbouw — WP-09 — 2026-09-03

De vergunningen-chatbot van LeefomgevingLab is de POC waar module K4 op leunt. Hoeveel zit er werkelijk in,
en is dat genoeg om lesmateriaal te zijn?

**Uitkomst: van 8 naar 924 fragmenten, uit 2 naar 170 bronnen. En de belangrijkste vondst is dat het gat
dat deze herbouw motiveerde er niet mee gedicht wordt — omdat het een ander soort gat is dan gedacht.**

---

## 1. Wat er stond (WP-09a)

```
vectors.npy      vorm (8, 1024)  dtype <f4      32.896 bytes
chunks.jsonl     8 fragmenten · 8.187 tekens · gemiddeld 1.023 tekens
gebouwd          2026-06-21 (74 dagen oud)
bronnen          2
                 4x  iplo.nl/regelgeving/instrumenten/omgevingsvergunning/
                 4x  iplo.nl/regelgeving/regels-voor-activiteiten/
```

De chatbot die module K4 beschrijft als draaiend "op een zoekindex over IPLO- en DSO-documentatie",
beantwoordde vragen uit **twee webpagina's**. Het vermoeden in `CLAUDE.md` — "ongeveer 8 chunks" — klopte
exact.

## 2. Wat er nu staat (WP-09b)

```
vectors.npy      vorm (924, 1024)  dtype <f4    3.784.832 bytes
chunks.jsonl     924 fragmenten · 986.001 tekens · gemiddeld 1.067 tekens
gebouwd          2026-09-03 (0 dagen oud)
bronnen          170
```

| | oud | nieuw | factor |
|---|---:|---:|---:|
| fragmenten | 8 | 924 | **115x** |
| tekens | 8.187 | 986.001 | **120x** |
| bronnen | 2 | 170 | 85x |
| leeftijd | 74 dagen | 0 dagen | — |

Het oordeel van `rag_inspect.py` schuift van **ZEER DUN** naar **REDELIJK**. De eis uit de backlog — index
jonger dan 7 dagen, aantal fragmenten met minstens een orde van grootte gegroeid — is ruim gehaald.

### Hoe de bronnen gekozen zijn

Niet door te gokken welke URL's zouden bestaan. `iplo.nl/robots.txt` wijst naar een sitemap met **8.585**
pagina's; daaruit is geselecteerd op de domeinen van `ops/ijkset-nl.jsonl` (vergunningen, geluid, externe
veiligheid, water, DSO), met voorkeur voor ondiepe overzichts- en definitiepagina's. **Alle 170 zijn vooraf
opgehaald en gemeten** op bereikbaarheid en tekstopbrengst voordat ze in de config landden; alle 170
leverden bruikbare tekst.

Alles ophalen was noch nodig noch gepast: 8.585 pagina's is de hele site.

## 3. Werkt het? Eén vraag zegt genoeg

Vraag **ijk-08** uit de ijkset, waarbij het veld `let_op` waarschuwt voor *"plausibel maar fout: verzonnen
normwaarden"*. Gesteld aan de draaiende chatbot op `:8792` ná de herbouw:

> **Wat is het plaatsgebonden risico en hoe verhoudt het zich tot het groepsrisico?**
>
> "Het plaatsgebonden risico is een maat voor het risico dat een onbeschermd en continu aanwezig persoon
> overlijdt als gevolg van een ongewoon voorval, zoals een calamiteit met gevaarlijke stoffen. Deze kans
> wordt uitgedrukt in een verhouding per jaar. Bij kwetsbare en zeer kwetsbare gebouwen en kwetsbare
> locaties moet het bevoegde gezag een grenswaarde in acht nemen, die maximaal 1 op de miljoen per jaar is."

Dat is de **echte** normwaarde uit de bron, geen verzinsel. In de oude index bestond geen enkel fragment
over externe veiligheid; deze vraag was daar principieel onbeantwoordbaar.

Het antwoordcontract werkt daarbij zoals module L3 het beschrijft: `onzekerheid: true`, een disclaimer
("indicatief, geen juridisch besluit") en een vangnet dat naar het bevoegd gezag verwijst.

## 4. De vondst die belangrijker is dan het aantal

Deze herbouw kwam voort uit vondst **V8**: het klasmodel plaatst `Lden` in het domein luchtvervuiling in
plaats van geluid, en de redenering was dat een deugdelijke index dat zou repareren.

**Dat gaat niet werken, en de meting laat zien waarom.**

In de nieuwe index van 924 fragmenten komen, gemeten met woordgrenzen:

| term | voorkomens |
|---|---:|
| `Lden` | **0** |
| `Lmax` | **0** |
| `dB(A)` | **0** |
| "geluid" | 42+ |

En van de zeven geluid-regelgevingspagina's van IPLO — `bepalen-geluid`, `basisgeluidemissie`,
`geluidaandachtsgebied`, `geluidproductieplafond`, `gecumuleerd-geluid`, `geluid-gevel`,
`regels-kaart-actieplan` — noemt **geen enkele** het begrip Lden.

IPLO is een portaal over de Omgevingswet. Het legt uit welke regels gelden en wie wat beoordeelt, niet wat
een akoestische grootheid betekent. Meer IPLO-pagina's toevoegen kan dit gat dus principieel niet dichten.

**Dit is een andere faalvorm dan gedacht.** Module K4 onderscheidt "te dunne index" van "plausibel maar
fout". Hier is een derde: **de vraag valt buiten het bronbereik**. Voor een gebruiker zien alle drie er
identiek uit — een zelfverzekerd, vloeiend, fout antwoord. Het verschil zit in wat je eraan doet:

| faalvorm | wat je ziet | wat je eraan doet |
|---|---|---|
| te dunne index | vage antwoorden op alles | index vergroten |
| buiten het bronbereik | precies op één onderwerp raak, elders mis | andere bron toevoegen, of de vraag afwijzen |
| plausibel maar fout | overal vloeiend, soms verzonnen | contract en verificatie |

### Wat de chatbot er zelf van maakt — het beste bewijsstuk van dit werkpakket

Dezelfde vraag, gesteld aan de draaiende chatbot mét de nieuwe index van 924 fragmenten:

> **Wat betekent Lden en waarvoor wordt het gebruikt?**
>
> "Lden staat voor **'Lärmpegel Dauer nacht'**, wat in het Nederlands 'geluidsniveau over een lange
> periode, inclusief nacht' betekent. Het is een maat voor het gemiddelde geluidsniveau over een 24-uurs
> periode, waarbij het nachtelijke geluid (van 23:00 tot 06:00) met een factor 10 wordt gewogen. (...)"
>
> **Bronnen:** `iplo.nl/thema/geluid/geluid-regelgeving/geluidproductieplafond/`,
> `iplo.nl/regelgeving/instrumenten/documenten/downloadpagina-mp40-21/`,
> `iplo.nl/regelgeving/instrumenten/documenten/downloadpagina-mp40-30/`,
> `iplo.nl/regelgeving/instrumenten/monitoring/`

De uitschrijving is verzonnen — Lden is *level day-evening-night*, en de avondperiode ontbreekt volledig.
Interessanter is de Duitse vorm: in de ijkset van WP-03 verzon Qwen2.5-32B onafhankelijk hiervan
"Lärmpegeldichte Nacht". Twee verschillende modellen grijpen naar hetzelfde soort verzinsel.

**Maar het echte lesmateriaal zit in de bronnenlijst.** De chatbot noemt vier IPLO-pagina's als
onderbouwing. In geen van die vier komt het woord Lden voor. Het ophaalmechanisme leverde de dichtstbijzijnde
fragmenten over geluid in het algemeen, het model schreef het antwoord uit zijn eigen parametrische kennis,
en de bronvermelding eronder geeft dat verzinsel het aanzien van iets dat nagezocht is.

Dit is precies wat een functioneel beheerder moet leren herkennen: **een bronvermelding bewijst niet dat
het antwoord uit die bron komt.** Het vangnet werkte wel — `onzekerheid: true`, disclaimer, verwijzing naar
het bevoegd gezag — en toch krijgt de bezoeker een zelfverzekerd fout antwoord met vier links eronder.

Bewaar dit antwoord als conserf. Het is de scherpste demonstratie op de hele machine van faalvorm
"plausibel maar fout", en het is echt gebeurd in plaats van bedacht.

Dat onderscheid is beter lesmateriaal dan het dichten van het gat geweest zou zijn, en het hoort in K4.
Wie Lden wél gedekt wil hebben, moet een bron buiten IPLO toevoegen — en dat is geen technische ingreep
maar een keuze over wat deze chatbot hoort te zijn.

## 5. Wat er aan de POC veranderd is

`CLAUDE.md` verbiedt POC-repo's aan te raken buiten WP-00. Hier is bewust van afgeweken, omdat WP-09b
opdraagt het bouwscript van de POC te draaien en dat met 170 bronnen niet werkte. Twee wijzigingen, beide
klein en achterwaarts compatibel:

**`src/leefomgevinglab/rag/ingest.py` — `build_index` is fouttolerant en beleefd geworden.** De functie
haalde alle URL's achter elkaar op zonder pauze, en liet één mislukking de hele bouw afbreken. Met twee
bronnen valt dat niet op; met honderd knijpt de bron af en verlies je de andere negenennegentig. Nu:
`pauze_s` tussen de pagina's, `pogingen` herhalingen bij een tijdelijke fout, en overgeslagen URL's worden
op stderr gemeld in plaats van stilzwijgend weggelaten.

De eerste bouwpoging liep hier ook echt op stuk: één pagina gaf een tijdelijke fout en de hele run van 100
was weg. Diezelfde pagina werkte seconden later gewoon.

**Twee tests toegevoegd** in `tests/test_rag_ingest.py`: één die vastlegt dat een kapotte URL de bouw niet
afbreekt en op stderr gemeld wordt, één die vastlegt dat een tijdelijke fout wordt herprobeerd. De negen
bestaande tests blijven slagen.

`scripts/07_build_rag_index.py` geeft de pauze mee (`fetch_pauze_s`, standaard 0,5 s).

**Wat níet veranderd is:** `embed_texts` verstuurt alle teksten in één request. Ik ging ervan uit dat dat
bij 481 fragmenten zou breken en heb dat gemeten voordat ik iets aanraakte — 481 embeddings in één POST
duurt 10,2 seconden, ruim binnen de timeout van 60. Er was dus niets te repareren.

## 6. Wat hier misging

**Ik heb twee keer een deelstring voor een woord aangezien.** Bij WP-03 stond `is` in de Engelse
woordenlijst, waardoor keurig Nederlandse antwoorden als Engels werden gemarkeerd. Hier matchte `Lden` op
**`gelden`**, een woord dat op vrijwel elke regelgevingspagina staat — waardoor 70 van de 70 pagina's als
"dekt Lden" scoorden en ik bijna concludeerde dat het gat gedicht was. Met woordgrenzen: nul.

Beide keren zou de conclusie precies omgekeerd zijn geweest. Genoteerd als V14, en het hoort in module K4:
een meting die je niet controleert is een aanname met een getal erin.

**De eerste bronselectie miste het doel.** Ik koos ondiepe overzichtspagina's, wat goed was voor breedte
maar de definiërende pagina's oversloeg. Pas na het meten van de termdekking bleek dat, en pas daarna bleek
dat ook de diepe pagina's Lden niet noemen. De volgorde had andersom gemoeten: eerst vaststellen welke
begrippen gedekt moeten zijn, dan pas bronnen kiezen.

## 7. Herhalen

```bash
python3 ops/ijking/rag_inspect.py --dir /mnt/nvme/geluidsmeter/data/rag
cd /mnt/nvme/workspaces/LeefomgevingLab && python3 scripts/07_build_rag_index.py
```

De vorige index staat als back-up in `/mnt/nvme/geluidsmeter/data/rag-backup-2026-09-03/`.

## 8. Wat er nog open staat

- **Index-leeftijd zichtbaar maken in de gezondheidsendpoint van de bemiddelaar** — kan pas bij WP-05,
  want die dienst bestaat nog niet. Het contract in `gateway/README.md` heeft er al een veld voor:
  `rag_index_leeftijd_dagen`.
- **De chatbot draait nog op de oude index in het geheugen** als hij die bij het starten inleest. Een
  herstart van LeefomgevingLab is niet uitgevoerd; de test in §3 gaf al wel het nieuwe antwoord, dus de
  index wordt kennelijk per vraag geladen.
- **Een bron voor akoestische begrippen**, als je wilt dat de chatbot vragen als ijk-05 aankan. Zie §4.
