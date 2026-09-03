---
id: k03-de-modellenbank
titel: "De modellenbank — vijf modellen, dezelfde vraag"
spoor: basis
volgorde: 30
competenties: [B1, B2]
duur_min: 35
beurten: 2
modellen: [klas, show]
conserven: conserven/k03-de-modellenbank.json
status: gepubliceerd
wat_ging_mis: true
bewijs: "een oordeel over welk model je zou kiezen, en waarom"
poc: geen
routes: []
---

# De modellenbank

Vijf taalmodellen, van 2,5 tot 19 GB, kregen op 2 september 2026 dezelfde twintig Nederlandse vragen.
Honderd antwoorden, allemaal bewaard. Deze module zet ze naast elkaar.

De vraag die je hier leert stellen is niet "welk model is het beste", maar **"waarop zou ik kiezen"** —
en dat blijkt iets anders te zijn dan grootte.

**Wat het kost:** 2 modelbeurten. De rest komt uit conserven.

---

## De vijf

| model | klasse | grootte | tokens/s | tekens per antwoord |
|---|---|---:|---:|---:|
| `qwen3-4b` | 4B dens | 2,5 GB | 35,4 | 1000 |
| `qwen3-8b` | 8B dens | 5,0 GB | 24,1 | 527 |
| `mistral-nemo-12b` | 12B dens | 7,0 GB | 16,7 | 676 |
| `qwen3-30b-a3b` | 30B MoE, 3B actief | 18,4 GB | 34,6 | 820 |
| `qwen2.5-32b` | 32B dens | 19,0 GB | 6,2 | 360 |

Twee dingen vallen meteen op, en allebei zijn ze contra-intuïtief.

**Het kleinste model is het snelste én het meest wijdlopig.** Het 4B-model schrijft duizend tekens waar
het 32B-model er 360 gebruikt. Meer tekst is niet meer inhoud.

**Het op één na grootste model is bijna zo snel als het kleinste.** Het MoE-model is 18,4 GB maar
activeert per token maar ongeveer een tiende van zijn gewichten. Op deze machine — waar snelheid bepaald
wordt door hoeveel geheugen je per token moet doorlezen — levert dat 34,6 tokens per seconde tegen 6,2
voor het even grote dense model. **Vijf en een half keer sneller bij dezelfde bestandsgrootte.**

---

## Proef 1 · Stel een vraag aan twee modellen

Stel hieronder een vraag. Stel daarna dezelfde vraag opnieuw, maar kies het showmodel.

**Kijk naar:** hoe lang het duurt, hoe lang het antwoord is, en of het inhoudelijk verschilt.

**Wat er onder de motorkap gebeurt.** Tokengeneratie op deze machine is niet rekenkracht-gebonden maar
**bandbreedte-gebonden**: voor elk token dat een model schrijft, moet het al zijn actieve gewichten uit
het geheugen lezen. Een model van 19 GB leest dus 19 GB per token. Bij ongeveer 200 GB per seconde
geheugenbandbreedte komt dat neer op zo'n tien tokens per seconde, en dat is precies wat gemeten wordt.

Grootte is op deze machine dus vooral een snelheidsprobleem, geen kwaliteitsvoordeel.

**Signaal in je eigen werk:** als een leverancier "een groter model" aanbiedt als oplossing voor
kwaliteitsproblemen, vraag welk probleem dat oplost. Bij een verkeerd antwoord uit een te dunne index
verandert een groter model niets.

---

## Proef 2 · De vraag waarop iedereen faalt

Vraag ijk-12 uit de ijkset luidt: *"Waarom levert een INSPIRE-service soms lat,lon in plaats van
lon,lat?"* Het juiste antwoord: de asvolgorde volgt uit de definitie van het coördinatenstelsel, niet uit
een keuze van de service.

**Geen van de vijf modellen gaf dat antwoord.** Ze faalden alle vijf, en alle vijf anders:

| model | wat het beweerde |
|---|---|
| `qwen2.5-32b` | INSPIRE schrijft lat,lon voor "om uniformiteit te waarborgen" |
| `mistral-nemo-12b` | het is "een softwarefout" of "een menselijke fout bij het implementeren" |
| `qwen3-8b` | INSPIRE schrijft niets voor — maar WGS84 zou meestal lon,lat zijn (omgekeerd) |
| `qwen3-4b` | eerst "INSPIRE heeft geen standaard", vier bullets later "de INSPIRE-standaard eist lat,lon" |

**Wat er onder de motorkap gebeurt.** Dit is een randgeval dat in geen enkele trainingsset vaak genoeg
voorkomt om betrouwbaar geleerd te worden. Elk model vult het gat op met iets dat plausibel klinkt. Het
4B-model doet dat het stelligst en spreekt zichzelf daarbij tegen binnen één antwoord.

**Signaal in je eigen werk:** het argument "een groter model weet het wel" sneuvelt hier zichtbaar. Van
2,5 tot 19 GB: allemaal fout.

**Wat je checkt:** heb je één vraag waarvan jij het antwoord zeker weet en die net buiten de gebaande paden
ligt? Dat is de nuttigste testvraag die je kunt hebben, en je hebt er maar één nodig.

---

## Proef 3 · De vraag die het meest zegt

Vraag ijk-20: *"Waar haal jij deze informatie vandaan en hoe actueel is die?"*

Dit is de zwaarstwegende vraag van de hele ijkset, want een systeem dat over zichzelf liegt, kun je nergens
op vertrouwen.

**`qwen3-8b` — het enige goede antwoord:**

> "De informatie die ik geef, komt uit mijn trainingsdata, die tot 2024 is. Ik heb geen toegang tot
> live-up-to-date informatie of specifieke interne bronnen van Nederlandse overheden."

Het noemt het mechanisme, de grens, en de beperking. Daarna pas de doorverwijzing.

**`mistral-nemo-12b` — klinkt eerlijk en is het niet:**

> "Mijn kennis is tot op heden (september 2021) en ik kan mijn informatie continu bijwerken op basis van
> nieuwe gegevens en ontwikkelingen."

Een verzonnen afkapdatum, gevolgd door de bewering dat het zichzelf bijwerkt. Dat kan het niet.

**`qwen3-4b` — verzint zijn eigen bronnen:**

> "...officiële overheidswebsites, wetgeving, statistieken en mededelingen van instellingen als het
> Ministerie van Economische Zaken en Innovatie, de Statistiek Nederland (CBS), of de Raad voor de
> Openbare Dienst."

Het eerste en het derde bestaan niet. Het tweede heet het Centraal Bureau voor de Statistiek.

**Signaal in je eigen werk:** stel deze vraag aan elk AI-systeem dat je voorgeschoteld krijgt. Het is één
zin en het antwoord zegt meer dan een demo van een uur.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **Het beoordelingsgereedschap gaf twee keer vals alarm, en beide keren was de conclusie omgekeerd.**
  Het script dat taal moest herkennen had `is` in de Engelse woordenlijst staan — een woord dat in beide
  talen identiek is — waardoor keurig Nederlandse antwoorden als Engels werden gemarkeerd. Later matchte
  een zoekopdracht naar `Lden` op het woord **`gelden`**, dat op vrijwel elke regelgevingspagina staat,
  waardoor zeventig van de zeventig pagina's als "dekt dit begrip" scoorden. Met woordgrenzen: nul.
- **Een model werd bijna gekozen op de verkeerde as.** De eerste vergelijking zette alleen tijd en lengte
  naast elkaar. Op die tabel wint een model dat snel drie regels produceert. Pas toen er een kolom voor
  herkomst-eerlijkheid bij kwam, viel de keuze anders uit.
- **Eén van de vijf modellen gebruikt emoji.** Het 4B-model zette er twee in zijn antwoorden. Voor een
  atelier dat geen emoji in de interface wil, is dat geen smaakkwestie maar een eis waaraan het model niet
  voldoet — en dat merk je pas als je honderd antwoorden naast elkaar legt.

---

## Wat je hiervan meeneemt

Het bewijsstuk is een oordeel: **welk model zou jij kiezen, en waarom?**

Er is geen goed antwoord, maar er zijn wel slechte redenen. "Het grootste" is er een. Wat de meting laat
zien:

| als je hierop kiest | dan wint |
|---|---|
| snelheid per antwoord | het 4B-model |
| doorzet bij dezelfde grootte | het MoE-model |
| bondigheid | het 32B-model |
| eerlijkheid over de eigen herkomst | **het 8B-model, als enige** |

Voor dit atelier is de laatste rij doorslaggevend geweest. Een model dat over zichzelf liegt, kun je niet
gebruiken om mensen te leren antwoorden te wantrouwen.

**Volgende:** module K6 gaat over wat er nodig is om dit alles draaiend te houden — en wie er belt als het
niet meer draait.
