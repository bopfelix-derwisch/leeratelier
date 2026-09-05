---
id: s03-de-verwachting
titel: "De verwachting — wat deze combinatie werkelijk oplevert"
spoor: sturing
volgorde: 30
competenties: [M1, M4, M6]
duur_min: 30
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "voor een eigen domein benoemd welk deel lokaal kan, welk deel cloud vraagt, en waarom"
poc: waterlab
routes: ["/#forecast", "/graphql", "/fews/rest/fewspiservice/v1/"]
---

# De verwachting

Dit is de kern van deze route. Alle andere modules gaan over wat er misgaat; deze gaat over wat er kan,
en waarom dat sinds kort iets anders is dan drie jaar geleden.

Deze module kost **geen modelbeurten**. Je kijkt naar een systeem dat draait.

**Open de case:** [de verwachtingstab van Waterlab](https://waterlab.felixisfelix.com/#forecast).

---

## De case in één alinea

Een veertiendaagse afvoer- en peilverwachting voor de IJssel. Live meetdata van RWS Waterinfo en een
weersverwachting van Open-Meteo gaan een statistisch recessiemodel met neerslag-impulsrespons in. Daar
komt een band uit: verwachte afvoer met een onzekerheidsmarge die breder wordt naarmate je verder
vooruitkijkt. Vervolgens schrijft een taalmodel daar een **interventieadvies** bij: wat betekent dit
peil voor de scheepvaart, voor de drinkwaterwinning, voor de landbouw, voor de natuur.

Dat draait op één apparaat ter grootte van een schoenendoos, gebouwd door één persoon.

---

## Wat deze case bewijst

Drie dingen, en ze zijn alle drie relevant voor een investeringsbesluit.

### 1. De modellenlaag kost geen licentie meer

Onder deze opstelling liggen open modellen en open data:

| onderdeel | wat het is | van wie |
|---|---|---|
| **wflow SBM** | hydrologisch model voor het stroomgebied | Deltares, open source |
| **Ribasim** | netwerkmodel voor de waterverdeling | Deltares, open source |
| **ERA5-Land** | historische weerdata voor de terugkijkscenario's | Copernicus, open data |
| **Copernicus DEM** | hoogtemodel | Copernicus, open data |
| **BRO / PDOK** | gemeten grondwaterstanden | Nederlandse overheid, open data |
| **Qwen2.5-32B** | het lokale taalmodel | open gewichten, draait op eigen hardware |

Wat je hier ziet, is een vakinhoudelijke keten waarvan **geen enkele schakel een licentie kost**. Dat is
de verschuiving. Tien jaar geleden zat de rekening in de modellen en de data; nu zit ze in de
**integratie** — het aan elkaar knopen, het draaiend houden, en de mensen die het snappen.

Voor een investeringsbesluit betekent dat iets concreets: als een leverancier u een prijs offreert,
vraag welk deel daarvan modellicentie is en welk deel integratie. Als het eerste bedrag hoog is, vraag
waarom, want het open alternatief is er meestal.

### 2. Lokaal en cloud is geen keuze maar een verdeling

Hier zit de architectuurbeslissing die het waard is om te herkennen. In dezelfde toepassing draaien
**twee soorten taalmodellen naast elkaar**, en dat is een bewuste verdeling:

| taak | model | waar | waarom daar |
|---|---|---|---|
| Spreiding van een ensemble duiden | Qwen2.5-32B | lokaal | veel aanroepen, weinig risico, data blijft staan |
| Kritieke knoop kiezen in het netwerk | Qwen2.5-32B | lokaal | idem, en het gebeurt in een lus |
| Grondwaterreeksen duiden | Qwen2.5-32B | lokaal | idem |
| **Het interventieadvies schrijven** | **Claude Haiku** | **cloud** | dit advies heeft operationele gevolgen |

Die laatste regel is de hele redenering, en ze staat ook zo opgeschreven in het project: de keuze voor
een cloudmodel is gemaakt *omdat het een advies is met potentiële operationele impact, waarvoor hogere
modelkwaliteit gewenst is.*

Dat is precies de afweging die je zelf moet maken, en ze is niet ideologisch. Je kiest niet tussen
lokaal en cloud. Je zet elk model daar waar zijn eigenschap telt:

- **lokaal** waar het vaak gebeurt, waar de gegevens niet weg mogen, en waar een fout goedkoop is;
- **cloud** waar het zelden gebeurt, waar het antwoord gevolgen heeft, en waar kwaliteit de doorslag geeft.

Een toepassing die alles lokaal doet, betaalt met kwaliteit op de plek waar dat het meeste kost. Een
toepassing die alles naar de cloud stuurt, betaalt met geld en met gegevens die de deur uitgaan. De
winst zit in de verdeling.

### 3. Agentisch betekent: het model kiest wat er berekend wordt

"Agentic" klinkt groot en is hier heel concreet. In de multimodel-proef gebeurt dit:

1. Een netwerkmodel rekent de waterverdeling over drie takken door.
2. Een taalmodel kijkt naar die uitkomst en **kiest welke knoop kritiek is**.
3. Voor precies dat deelstroomgebied worden vervolgens vijf gedetailleerde modelruns gestart.

Het model produceert dus geen tekst maar een **besluit over wat de machine hierna gaat doen**. Dat is
het verschil tussen een taalmodel als schrijfhulp en een taalmodel als regelaar.

Daar zit de winst én het risico, en allebei horen op je besluitkaart. De winst: je hoeft niet alles door
te rekenen, alleen wat ertoe doet — dat scheelt op deze hardware het verschil tussen wel en niet
haalbaar. Het risico: als de keuze van die knoop fout is, is alles wat erna komt keurig uitgerekende
onzin, en dat ziet er in het dashboard precies hetzelfde uit.

**De vraag die daarbij hoort:** wordt vastgelegd wat het model heeft gekozen en waarom? Kun je achteraf
reconstrueren waarom er die dag naar díé knoop is gekeken? Bij een advies met operationele gevolgen is
dat geen luxe.

---

## Waarom dit voor een bestuurder interessant is

Niet omdat er AI in zit. Omdat de drempel is verdwenen.

| | |
|---|---|
| **Hardware** | één edge-apparaat, ordegrootte tweeduizend euro, eenmalig |
| **Modellen en data** | open source en open data, geen licentie |
| **Bouwtijd** | één persoon, maanden, naast ander werk |
| **Aansluiting** | spreekt **FEWS PI REST 1.25**, het protocol van de bestaande sector |

Die laatste regel is de belangrijkste voor uw landschap. Dit is geen systeem dat het bestaande wil
vervangen; het praat de taal van wat er al staat. Een bestaande FEWS-client kan erop aansluiten alsof
het een gewone dienst is. Daarnaast liggen dezelfde gegevens klaar via een gewone REST-koppeling en via
een GraphQL-laag — drie ingangen, één datapad eronder.

Dat is wat een verkenning tegenwoordig kost, en dat is het echte nieuws. **De vraag is niet meer of het
technisch kan of wat de licenties kosten. De vraag is of je organisatie het kan onderhouden en of je het
antwoord kunt vertrouwen.** Precies daarom gaat de rest van deze route daarover.

---

## Wat hier misging

En nu het tegenwicht, want dit is een proefopstelling en geen product.

**De live verwachting die je hierboven opent, vertrekt op dit moment vanaf een verzonnen getal.**

De laatste echte meting bij Westervoort dateert van 30 augustus 2026: 71,4 m³/s. De zes dagen daarna
staan in de reeks op exact **400,0** — een opvulwaarde uit de code, die intreedt als de meetreeks gaten
heeft. De verwachting vertrekt vanaf dat getal en komt uit op 443,9 m³/s. Dat is **ruim zes keer** de
laatste werkelijke meting.

Drie dingen gingen tegelijk mis, en ze versterken elkaar:

1. Het veld dat aangeeft of er data beschikbaar is, staat gewoon op **waar**. Het telt namelijk of er
   vijf metingen in vijfendertig dagen zitten — niet of de **recente** dagen er zijn.
2. Het dashboard toont dat veld sowieso niet aan de bezoeker.
3. En 400 is een plausibel getal voor de IJssel. Was de opvulwaarde 9999 geweest, dan had iedereen het
   binnen een dag gezien.

Dit is dezelfde les als in de rest van de route, maar nu op de plek waar het het meeste pijn doet: **in
de module die de businesscase moet maken.** De potentie hierboven is echt. De uitvoering is op dit
moment onbetrouwbaar. Allebei waar, tegelijk.

Voor uw besluit is dat de nuttigste observatie van deze hele route. Wat u in een demo ziet, is de
potentie. Wat u koopt, is de uitvoering. Tussen die twee zit het werk waar niemand het over heeft, en
dat werk staat zelden in de offerte.

*(Een tweede, kleinere: de README van dit project zegt "geen licentie van toepassing", terwijl er een
Apache-2.0-licentiebestand naast ligt. Twee bronnen die elkaar tegenspreken over de vraag wat u met de
code mag. Zie ook S6.)*

---

## Opdracht

Voor één proces in uw eigen domein:

1. Welk deel zou lokaal kunnen draaien — vaak, goedkoop, met gegevens die niet weg mogen?
2. Welk deel verdient een duurder cloudmodel, omdat het antwoord gevolgen heeft?
3. Waar zou een model mogen **kiezen wat er vervolgens gebeurt**, en waar absoluut niet?

Vraag 3 is de nieuwe vraag. Vijf jaar geleden bestond ze niet, en op de meeste besluitkaarten staat ze
nog steeds niet.
