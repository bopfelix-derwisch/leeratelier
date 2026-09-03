---
id: w03-casussen
titel: "Casussen — wat validatie wel en niet bewijst"
spoor: waterlab
volgorde: 30
competenties: [B2, B6]
duur_min: 30
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de uitspraak geformuleerd die je op grond van een validatie wél mag doen"
poc: waterlab
routes: ["/api/validation", "/api/validation/hindcast", "/api/grondwater"]
---

# Casussen

Drie gebeurtenissen worden in het Waterlab nagespeeld, en één koppeling laat zien wat er gebeurt als je
twee bronnen naast elkaar legt.

De vraag van deze module: **wat mag je zeggen als een model een historische gebeurtenis goed naspeelt?**

Deze module kost **geen modelbeurten**.

---

## De drie casussen

| casus | periode | wat het laat zien |
|---|---|---|
| **Hoogwater januari 1995** | dec 1994 – jan 1995 | gedrag onder extremen, met een gesynthetiseerde instroom |
| **Droogte zomer 2018** | zomer 2018 | laagwater, en de koppeling met grondwater |
| **Hoogwater juli 2021** | mei – aug 2021 | gemeten instroom náást een synthetische — hetzelfde model, twee invoeren |

De derde is de interessantste, want daar is de invoer de enige variabele.

---

## Proef 1 · Dezelfde vraag, twee invoeren

Bij 2021 draait het model twee keer: één keer met de **gemeten** instroom bij Westervoort, één keer met een
**synthetische**.

**Wat je doet:** vergelijk de twee uitkomsten.

**Wat er onder de motorkap gebeurt.** Het model, het gebied, de neerslag en de periode zijn identiek.
Alleen de randvoorwaarde verschilt. Het verschil in uitkomst is dus volledig toe te schrijven aan die ene
invoer — en dat maakt zichtbaar hoeveel van je resultaat door je randvoorwaarde bepaald wordt in plaats van
door je model.

**Signaal in je eigen werk:** als iemand een modeluitkomst presenteert, vraag welke invoer die uitkomst het
sterkst bepaalt. Vaak is dat niet het model waar de presentatie over gaat.

**Wat je checkt:** is er ooit gedraaid met een alternatieve invoer om te zien hoeveel dat uitmaakt? Zo niet,
dan weet niemand hoe gevoelig het resultaat is.

---

## Proef 2 · Wat een skill-score wel en niet zegt

Open `/api/validation`. Per meetpunt staan er objectieve scores: NSE, KGE, Pearson r, bias.

**Wat er onder de motorkap gebeurt.** Deze getallen vergelijken de simulatie met de meting over de
gesimuleerde periode. Een hoge score betekent: dit model reproduceert déze gebeurtenis goed, met déze
invoer, op déze punten.

Het betekent **niet** dat het model de volgende gebeurtenis goed voorspelt. Een hindcast — het naspelen
van iets dat al gebeurd is — kan bijgesteld zijn tot hij klopt, zonder dat iemand dat kwaad bedoelt.

**Signaal in je eigen werk:** "gevalideerd" is een woord dat zonder aanvulling niets betekent. Gevalideerd
waarop, over welke periode, tegen welke onafhankelijke meting?

**Wat je checkt:** was de validatiedata onafhankelijk van de data waarmee gekalibreerd is? Als dat niet zo
is, meet de validatie hoe goed het model onthouden heeft, niet hoe goed het voorspelt.

---

## Proef 3 · Twee bronnen naast elkaar

Bij de droogte van 2018 worden gemeten grondwaterstanden uit het BRO, opgehaald via PDOK, naast de
IJsselstanden gelegd.

**Wat je ziet:** een verband met vertraging — het grondwater volgt de rivier, maar later.

**Wat er onder de motorkap gebeurt.** Twee onafhankelijke bronnen die hetzelfde verhaal vertellen, geven
meer vertrouwen dan één bron die het heel precies vertelt. Dat is het sterkste argument dat een keten kan
leveren, en het kost geen modellering — alleen de bereidheid om een tweede bron erbij te halen.

Maar let op wat er níet staat: dat het één het ander veroorzaakt. Een verband met vertraging is een
verband met vertraging.

**Signaal in je eigen werk:** een dashboard dat twee reeksen over elkaar legt en de kijker het verband laat
maken. Dat is nuttig én het is de plek waar overinterpretatie ontstaat.

**Wat je checkt:** staat er bij een verband of het gemeten, berekend of verondersteld is?

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De 1995-casus rust op een instroom die niet gemeten is.** Vóór 2000 bestaat de reeks niet; hij is
  afgeleid uit het RIZA-archief. Op het dashboard staat dat erbij, maar wie alleen de grafiek ziet, ziet
  het niet.
- **De piekwaarden van 1995 en 2021 zijn niet vergelijkbaar.** Andere periode, andere instroom, andere
  modelinstellingen — bij 1995 een warme start met sneeuw aan, bij 2021 een koude start zonder sneeuw. Twee
  getallen naast elkaar zetten zou een conclusie opleveren die nergens op slaat.
- **Validatie is hier eerlijk gedaan en dat is de uitzondering.** Er staat expliciet bij dat er alleen
  gescoord wordt waar een onafhankelijke meting beschikbaar is. Dat is de goede praktijk, en het valt op
  dat het opgeschreven moest worden.

---

## Wat je hiervan meeneemt

Het bewijsstuk van deze module is een formulering: **welke uitspraak mag je doen op grond van een
validatie?**

| wat er vaak gezegd wordt | wat je ervan mag maken |
|---|---|
| "het model is gevalideerd" | "het reproduceert deze gebeurtenis, op deze punten, met deze invoer" |
| "de score is 0,9" | "over deze periode, tegen deze meting, die onafhankelijk was" |
| "twee bronnen bevestigen elkaar" | "twee bronnen vertonen een verband; oorzaak is daarmee niet aangetoond" |
| "het model voorspelt X" | "het model geeft X, gegeven een randvoorwaarde die zelf een schatting is" |

De rechterkolom is langer. Dat is geen slordigheid van de taal maar de prijs van precisie, en het is
precies het werk van een functioneel beheerder: de linkerkolom horen en de rechterkolom opschrijven.

**Volgende:** dit was de laatste module van spoor W. Als je de basisroute nog niet af hebt, ga dan verder
met K7 en vul je beheerkaart in — dat is waar dit allemaal naartoe werkt.
