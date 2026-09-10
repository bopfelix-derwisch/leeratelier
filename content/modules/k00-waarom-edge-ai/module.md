---
id: k00-waarom-edge-ai
titel: "Waarom hier, en niet in de cloud"
spoor: basis
volgorde: 5
competenties: [B1, B4, B6]
duur_min: 25
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de vijf afwegingsvragen beantwoord voor je eigen toepassing"
poc: geen
routes: []
---

# Waarom hier, en niet in de cloud

Alles wat je in dit atelier ziet draait op één computer ter grootte van een schoenendoos, in een woonkamer.
Geen datacentrum, geen abonnement, geen verbinding naar buiten voor de antwoorden.

Deze module gaat over waarom, en vooral over wanneer dat een verstandige keuze is en wanneer niet.

Deze module kost **geen modelbeurten**. Ze is de inleiding op de rest.

---

## Kijk eerst wat er op zo'n kastje past

Voordat je de afweging leest, is het nuttig om te zien waar het over gaat.

**Open [de verwachting van Waterlab](https://waterlab.felixisfelix.com/#forecast)** en laat hem even
staan. Je ziet een veertiendaagse afvoer- en peilverwachting voor de IJssel: gemeten waarden uit de
live meetnetten van Rijkswaterstaat, een weersverwachting erbij, een band die breder wordt naarmate je
verder vooruitkijkt, en eronder een advies over wat dit peil betekent voor scheepvaart, drinkwater,
landbouw en natuur.

Dat draait op dezelfde machine als waar je nu op leest.

**Vijf vragen om bij je te houden terwijl je kijkt.** Ze komen verderop in deze module allemaal terug,
en op je beheerkaart nog een keer.

1. **Wat hiervan moet lokaal?** De meetreeksen zijn openbaar. De modellen zijn openbaar. Is er iets in
   dit scherm dat de deur niet uit mag — en zo niet, waarom staat het dan toch hier?
2. **Wat hiervan kán niet lokaal?** Ergens in deze keten wordt een taalmodel in de cloud aangeroepen.
   Kun je raden welk onderdeel dat is, en waarom juist dat?
3. **Wat kost dit?** Er zit geen abonnement op en geen prijs per vraag. Wat is dan de rekening, en aan
   wie wordt die gestuurd?
4. **Wat gebeurt er als de verbinding wegvalt?** Welke helft van dit scherm blijft werken, en welke
   helft is dan leeg?
5. **Wie merkt het als dit niet meer klopt?** Niet: wie repareert het. Wie **merkt** het.

Vraag vijf is de lastigste, en niet toevallig. Er staat op dit moment iets in dat scherm dat níét klopt,
al maanden, en het valt niet op omdat het er plausibel uitziet. Wat het is, staat onderaan deze module
bij *Wat hier misging* — kijk eerst zelf of je het vindt.

---

## Wat "edge AI" is

Geen productcategorie en geen technologie. Het is één keuze: **waar staat de rekenkracht ten opzichte van
de gegevens.**

| | de gegevens gaan naar de rekenkracht | de rekenkracht staat bij de gegevens |
|---|---|---|
| heet | cloud | edge |
| jouw vraag gaat | naar een datacentrum | nergens heen |
| je betaalt | per vraag | eenmalig, plus stroom |
| werkt zonder internet | nee | ja |
| wie houdt het draaiend | de leverancier | jij |

Die laatste rij is de rij die in verkoopgesprekken het minst aan bod komt en in beheer het meest.

---

## De opstelling hier

Eén NVIDIA Jetson AGX Orin met 61 GB geheugen dat processor en grafische kaart **delen**. Daarop draaien
tegelijk:

| model | rol | grootte |
|---|---|---:|
| Qwen3-8B | het model dat je vragen beantwoordt | 5,0 GB |
| Qwen2.5-32B | het trage vergelijkingsmodel | 19,0 GB |
| bge-m3 | zet tekst om in getallen voor de zoekindex | 1,1 GB |

Gemeten op deze machine: het eerste model haalt 24 tokens per seconde, het derde 6,2. Alle modellen samen
beslaan 77 GB op schijf.

**Waarom dat verschil in snelheid?** Niet door rekenkracht maar door geheugenbandbreedte. Voor elk woord
dat een model schrijft, moet het al zijn actieve gewichten door het geheugen halen. Een model van 19 GB
leest dus 19 GB per woord. Bij ongeveer 200 GB per seconde kom je dan op een handvol woorden per seconde,
en dat is precies wat gemeten wordt.

Dat is de kern van edge: je koopt geen snelheid, je koopt onafhankelijkheid.

---

## Dezelfde toepassing, twee tegenovergestelde keuzes

Dit is de interessantste vergelijking op deze machine, want het gaat om **hetzelfde programma**.

Derwisch is een dagelijkse gesproken reflectie: je drukt op een knop, spreekt in, en krijgt een antwoord
terug. Die toepassing draait hier in twee smaken.

| | **orin3** | **reTerminal / reComputer** |
|---|---|---|
| inferentie | lokaal, drie modellen | **geen** — API's naar buiten |
| apparaat | ontwikkelmachine, geen scherm | ePaper-kiosk, geen pc eromheen |
| gegevens | blijven in de machine | gaan het net op |
| kosten | eenmalig plus stroom | per vraag |
| zonder internet | werkt | werkt niet |
| beheerlast | hoog: modellen, geheugen, updates | laag |
| wat je ervoor terugkrijgt | volledige controle | een apparaat dat je ophangt en vergeet |

**Geen van beide is de goede keuze.** Ze zijn allebei goed, voor verschillende dingen. Het apparaat aan de
muur hoeft niet te weten hoe een taalmodel werkt; de ontwikkelmachine moet dat wel.

### En dan de nuance die je makkelijk mist

Ook de lokale opstelling praat met de cloud. De keten is:

```
knop op orin3  →  opname  →  spraak-naar-tekst  →  lokaal taalmodel
               →  Vercel-relay  →  Upstash KV  →  reTerminal-scherm
```

De **inferentie** is lokaal. De **verbinding** loopt via twee clouddiensten, want het schermpje aan de
muur kan orin3 niet rechtstreeks bereiken. Er gaat geen enkele vraag naar een extern taalmodel, en toch is
dit geen gesloten systeem.

**"Lokaal" is zelden absoluut.** De nuttige vraag is niet of iets lokaal draait, maar *welk deel* lokaal
draait en welk deel niet.

---

## De afweging: vijf vragen

Hier gaat het om. Niet om specificaties, maar om welke vraag je stelt voordat iemand hardware koopt.

### 1. Moet de data binnen blijven?

Als het antwoord ja is, is de afweging klaar en zijn de andere vier vragen alleen nog invulling. Als het
antwoord "eigenlijk niet, maar het voelt beter" is, is het geen ja — en dan betaal je de beheerlast voor
een gevoel.

*Hier:* geen enkele vraag verlaat de machine. Voor een lab met beleidsdilemma's is dat het hele punt.

### 2. Hoe snel moet het antwoord er zijn?

Edge wint bij millisecondes — een camera die iets moet herkennen voordat het voorbij is. Bij een gesprek
van enkele seconden wint edge niet: een clouddienst met een groot model is dan meestal sneller dan een
kleine machine met een klein model.

*Hier:* een antwoord duurt vier tot vijfentwintig seconden. Dat is voor lesmateriaal prima en voor een
gebruiker die op een knop drukt ook. Voor een chatbot op een gemeentesite zou het te traag zijn.

### 3. Wat kost het per vraag?

Cloud rekent per vraag; edge rekent eenmalig plus stroom. Er is een omslagpunt, en dat ligt lager dan
mensen denken zodra het gebruik meevalt.

*Hier:* het atelier heeft een dagbudget van 300 antwoorden. Bij dat volume is de hardware allang
terugverdiend — maar de hardware stond er al, en dat is precies wat de rekensom vertekent.

### 4. Wie houdt het draaiend?

Dit is de vraag die het vaakst vergeten wordt en het vaakst beslissend blijkt.

*Hier:* één persoon. Modellen bijwerken, geheugen bewaken, kijken of de index niet stilstaat. Elke
storing wacht tot die persoon tijd heeft. Dat staat ook zo op de inlogpagina, en het is de eerlijkste zin
van het hele atelier.

### 5. Wat gebeurt er als de verbinding wegvalt?

Bij edge: niets, het rekent door. Bij cloud: het stopt. Omgekeerd: valt de **machine** weg, dan is bij
edge alles weg en bij cloud alleen jouw kant.

*Hier:* de reTerminal aan de muur werkt niet zonder internet. Orin3 wel — maar de reTerminal krijgt zijn
antwoorden dan niet meer te zien.

---

## De alternatieven, kort

| | wanneer je dit kiest |
|---|---|
| **Jetson** (hier) | je wilt echte taalmodellen lokaal draaien en hebt iemand die het beheert |
| **Raspberry Pi met een versneller** (Hailo, Coral) | beeldherkenning of geluidsclassificatie aan de rand; te klein voor taalmodellen van deze omvang |
| **Laptop of pc met NPU** | ontwikkelen en uitproberen; niet iets wat permanent moet draaien |
| **Clouddienst per vraag** | wisselend gebruik, geen beheercapaciteit, data mag naar buiten |
| **Eigen GPU-server** | veel gebruik, data moet binnen de organisatie blijven, er is een beheerteam |
| **Kiosk zonder inferentie** (de reTerminal) | het apparaat hoeft alleen te tonen; het rekenwerk staat ergens anders |

De laatste rij is een categorie die vaak vergeten wordt. Een apparaat aan de rand hoeft niet zelf te
rekenen om nuttig te zijn.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **Twee grote modellen passen niet naast elkaar, en dat bleek pas bij een poging.** Het geheugen is
  gedeeld tussen processor en grafische kaart, en bij het laden van een tweede model van 18 GB naast het
  bestaande van 19 GB bleef er 0,5 GB over. Het laden lukte alleen na het legen van de schijfcache, want
  het geheugenbeheer van deze chip kan die cache niet zelf opeisen. De foutmelding was
  `cudaMalloc failed: out of memory` — technisch waar en weinig behulpzaam.
- **Een bekende softwarefout maakte een hele modelklasse onbruikbaar.** Modellen van het type
  "mixture-of-experts" — op papier ideaal voor deze machine — bleven hangen op precies deze chip. De
  oorzaak lag niet in het model maar in één regel in de grafische bibliotheek. Die is teruggedraaid, maar
  de onderliggende fout in het besturingssysteem zit er nog steeds, en bij elke update moet opnieuw
  gecontroleerd worden of hij terugkomt. Dat is beheerlast die je niet inkoopt maar erft.
- **De eerste kostenraming zat er een factor twintig naast.** Een script berekende dat de machine 3225
  antwoorden per dag aankon. Dat klopte alleen als hij dag en nacht op volle kracht draait, alleen voor
  het atelier, terwijl hij gedeeld wordt met andere toepassingen. Het werkelijke budget staat op 300.
- **En het antwoord op vraag vijf hierboven.** De verwachting van Waterlab die je aan het begin hebt
  opengeklikt, vertrekt vanaf een verzonnen getal. De laatste echte meting bij Westervoort dateert van
  30 augustus: 71,4 m³/s. De dagen daarna staan op exact **400,0** — een opvulwaarde die de code
  invult als er gaten in de meetreeks zitten. De verwachting begint daardoor op 443,9 m³/s, ruim zes
  keer de laatste werkelijke meting. Het veld dat zegt of er data beschikbaar is, staat gewoon op
  *waar*: het telt of er vijf metingen in vijfendertig dagen zitten, niet of de **recente** dagen er
  zijn. En 400 is een geloofwaardig getal voor de IJssel — was de opvulwaarde 9999 geweest, dan had
  iedereen het binnen een dag gezien. Niemand merkte het, en dat is precies waarom vraag vijf niet gaat
  over wie het repareert.
- **De oorspronkelijke opzet noemde andere hardware.** In een eerdere overdracht stond een Raspberry Pi
  met een Hailo-versneller als richting. Dat is verlaten toen bleek dat taalmodellen van deze omvang daar
  niet op passen. Zulke koerswijzigingen staan zelden in een eindrapport, en ze zijn juist het leerzaamst.

---

## Wat je hiervan meeneemt

De vijf vragen, voor je eigen toepassing:

| vraag | jouw antwoord |
|---|---|
| Moet de data binnen blijven — en is dat een eis of een gevoel? | |
| Hoe snel moet het antwoord er zijn? | |
| Wat kost één antwoord, en bij welk volume kantelt dat? | |
| Wie houdt het draaiend, en wat gebeurt er als die persoon weg is? | |
| Wat werkt er nog als de verbinding wegvalt? En als de machine wegvalt? | |

En de vraag die onder alle vijf ligt: **welk deel draait lokaal, en welk deel niet?** Vrijwel geen enkele
opstelling is helemaal het een of het ander, en de scheidslijn is waar je beheer en je risico's zitten.

**Volgende:** module K1, de rondgang. Daar zie je wat er op deze ene machine allemaal tegelijk draait.
