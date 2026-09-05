---
id: k02-de-motorkap-zonder-mystiek
titel: "De motorkap zonder mystiek"
spoor: basis
volgorde: 20
competenties: [B1]
duur_min: 30
beurten: 2
modellen: [klas]
conserven: conserven/k02-de-motorkap-zonder-mystiek.json
status: gepubliceerd
wat_ging_mis: true
bewijs: "de zes onderdelen van je eigen toepassing benoemd"
poc: leefomgevinglab
routes: ["/openapi.json", "/chatbot"]
---

# De motorkap zonder mystiek

"AI" is geen onderdeel. Het is een verzamelnaam voor zes dingen die elk apart kunnen breken, elk een
eigen eigenaar hebben, en elk op een andere manier verouderen.

Deze module benoemt die zes. Daarna kun je van elke toepassing die je tegenkomt zeggen welk stukje het
over heeft — en, belangrijker, welk stukje niemand beheert.

**Wat het kost:** 2 modelbeurten.

---

## Wat je gaat zien

| onderdeel | wat het doet | wat er misgaat als het verouderd is |
|---|---|---|
| **bron** | de tekst of data waar het over gaat | het antwoord gaat over vorig jaar |
| **bewerking** | knipt de bron in stukken | stukken vallen midden in een zin |
| **embeddings** | zet elk stuk om in getallen | zoeken vindt de verkeerde stukken |
| **index** | bewaart die getallen | staat stil terwijl de bron doorloopt |
| **prompt** | de instructie aan het model | niemand weet meer wat erin staat |
| **model** | schrijft de zinnen | verzint aan wat er niet gevonden is |

Het contract waarlangs die onderdelen met elkaar praten, staat in de
**OpenAPI-beschrijving** die de POC zelf publiceert. Die kun je openen; dat doe je in
[proef 3 hieronder](#proef-3-kijk-zelf-in-de-motor).

De volgorde is de volgorde waarin een vraag er doorheen gaat. Het model is het **laatste** onderdeel,
niet het eerste — en dat is precies andersom dan hoe erover gepraat wordt.

---

## Proef 1 · Het model is niet de kennis

Stel de chatbot een vraag over iets in de documentatie. Stel daarna dezelfde vraag anders geformuleerd.

**Kijk naar:** verandert het antwoord van inhoud, of alleen van formulering?

**Wat er onder de motorkap gebeurt.** Je vraag wordt eerst omgezet in getallen — een *embedding* — en
vergeleken met de getallen van elk opgeslagen tekststuk. De vier best passende stukken gaan mee naar het
model, samen met een instructie. Het model schrijft dan een antwoord dat bij die stukken past.

Op deze machine zijn dat concrete getallen:

| | |
|---|---|
| embeddingmodel | `bge-m3`, 1,1 GB, poort 8082 |
| dimensies | 1024 getallen per tekststuk |
| stukgrootte | 1200 tekens, met 200 tekens overlap |
| stukken opgehaald per vraag | **4** |
| taalmodel | `Qwen3-8B`, 5 GB, poort 8081 |

Vier stukken. Dat is het hele geheugen waaruit een antwoord wordt geschreven.

**Signaal in je eigen werk:** iemand zegt "we hebben ons model getraind op onze documenten". Vraag dan of
ze het model getraind hebben of een index gebouwd. Het tweede is bijna altijd het geval, en het is iets
heel anders: bij een index zit jouw kennis náást het model, niet erin.

**Wat je checkt:** hoeveel stukken worden er per vraag opgehaald, en hoe groot is een stuk? Twee getallen.
Ze bepalen samen wat het model überhaupt kán weten van jouw documenten.

---

## Proef 2 · De prompt is een tekst die iemand ooit schreef

Vraag de chatbot iets waarop hij niet kan of mag antwoorden — vraag om een juridisch oordeel.

**Kijk naar:** de disclaimer en de verwijzing. Waar komen die vandaan?

**Wat er onder de motorkap gebeurt.** Ze staan als vaste tekst in de broncode. Er is geen model dat
besluit voorzichtig te zijn; er is een programmeur geweest die een zin heeft opgeschreven. In dit systeem
staat er letterlijk:

```python
{"vraag": activiteit, "bron": BRON, "onzekerheid": True,
 "disclaimer": DISCLAIMER, "vangnet": VANGNET}
```

Dat is de hele voorzichtigheid: drie constanten en een vaste `True`.

**Signaal in je eigen werk:** als de toon van een systeem verandert na een update zonder dat iemand het
model heeft aangeraakt, is de prompt gewijzigd. Dat is een tekstbestand, en tekstbestanden hebben een
eigenaar en een versiegeschiedenis — of ze horen die te hebben.

**Wat je checkt:** waar staat de prompt, wie mag hem wijzigen, en zit hij in versiebeheer? Als het antwoord
op de laatste vraag nee is, kan niemand nagaan waarom het systeem vorige week anders antwoordde.

---

## Proef 3 · Kijk zelf in de motor

Open de OpenAPI-beschrijving van LeefomgevingLab:
**[`/openapi.json`](https://leefomgevinglab.felixisfelix.com/openapi.json)**.

Dat is de technische beschrijving die de POC zelf publiceert: elk pad, elke parameter, elk
antwoordveld.

**Kijk naar:** het veld `info.title`, en daarna naar de lijst met paden.

**Wat er onder de motorkap gebeurt.** Dit bestand wordt automatisch gegenereerd uit de code. Het is dus
niet documentatie die iemand bijhoudt maar een afdruk van wat er werkelijk draait — en daarmee het
eerlijkste document dat een API heeft.

**Signaal in je eigen werk:** een leverancier die geen OpenAPI-beschrijving kan leveren, heeft die
waarschijnlijk niet, en dan is de documentatie een apart document dat kan afwijken van de werkelijkheid.

**Wat je checkt:** vraag om de OpenAPI-specificatie en doe er één echte aanroep mee. Dat is de goedkoopste
controle die er bestaat, en op deze machine is die les duur betaald — zie hieronder.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De titel in `/openapi.json` klopte maandenlang niet.** Het project heette ooit "Geluidsmeter" en is
  hernoemd toen geluid één van meerdere onderwerpen werd. In de gegenereerde beschrijving stond
  `Geluidsmeter API` — zichtbaar voor iedereen die het bestand opende, en juist dit is het bestand waarvan
  je aanneemt dat het klopt omdat het automatisch gegenereerd is. Op 3 september 2026 gecorrigeerd.
- **Een gegokt endpoint bestond niet.** Uit de kwaliteitspagina van de POC zelf: *"Het gegokte operatie-pad
  bestond niet; de echte is `werkzaamheden/_bepaalRegelbeheerobjectTyperingen` (POST)."* De conclusie die
  daar als terugkerend patroon staat: eerst de spec, dan één echte aanroep, dan pas bouwen.
- **`onzekerheid` is nooit berekend.** Het staat op vier plaatsen in de broncode als vaste `True`. Het
  systeem meldt dus evenveel twijfel bij een antwoord dat woordelijk uit een fragment komt als bij een
  antwoord dat het model volledig zelf bedacht heeft.

---

## Wat je hiervan meeneemt

Het bewijsstuk: **de zes onderdelen van je eigen toepassing**, met per onderdeel een naam en een eigenaar.

| onderdeel | wat is het bij ons | wie beheert het | wanneer voor het laatst bijgewerkt |
|---|---|---|---|
| bron | | | |
| bewerking | | | |
| embeddings | | | |
| index | | | |
| prompt | | | |
| model | | | |

Lege vakjes zijn het interessantst. Een onderdeel zonder eigenaar is een onderdeel dat niemand bijwerkt,
en dat wordt vanzelf het onderdeel dat stukgaat.

**Volgende:** module K3 zet vijf modellen naast elkaar op dezelfde vraag. Dan zie je wat het laatste
onderdeel — het model zelf — nu eigenlijk toevoegt.
