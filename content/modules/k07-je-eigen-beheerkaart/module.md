---
id: k07-je-eigen-beheerkaart
titel: "Je eigen beheerkaart"
spoor: basis
volgorde: 70
competenties: [B4, B6]
duur_min: 30
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "een ingevulde beheerkaart over je eigen toepassing of bron"
poc: geen
routes: []
---

# Je eigen beheerkaart

Dit is waar je mee weggaat. Eén A4 over jouw toepassing of jouw bron, dat je maandag op tafel kunt leggen.

Geen architectuurnotitie, geen adviesrapport. Zes vragen, en de meeste antwoorden zijn één regel.

Deze module kost **geen modelbeurten**. Er wordt niets bewaard: je vult in, je downloadt, en daarna is het
weg bij ons.

**[Ga direct naar het formulier](/beheerkaart)**

---

## Waarom deze zes vragen

| # | de vraag | waarom hij erin staat |
|---|---|---|
| 1 | Wat gaat hier het eerst mis? | drie realistische faalvormen dwingen tot kiezen |
| 2 | Waaraan merk ik het? | het signaal, niet de oorzaak — want de oorzaak zie je nooit als eerste |
| 3 | Wat check ik dan? | uitvoerbaar zonder ontwikkelaar, anders is het geen check maar een verzoek |
| 4 | Wanneer is het niet meer mijn probleem? | een escalatiepunt dat je vooraf kiest, kies je rustiger |
| 5 | Wat vraag ik mijn leverancier? | drie vragen, mee te nemen naar het eerstvolgende gesprek |
| 6 | Waar neemt het model het denken over? | de enige vraag die niet over techniek gaat |

De eerste vijf zijn beheer. De zesde is oordeelsvorming, en die is de reden dat deze route bestaat.

---

## Proef 1 · Kies de waarschijnlijkste, niet de ergste

Bij vraag 1 is de verleiding om het rampscenario op te schrijven: het systeem ligt eruit, de data lekt, de
gemeente staat in de krant.

**Doe dat niet.** Schrijf op wat er waarschijnlijk als eerste misgaat. Uit deze route:

- de index staat stil terwijl de bron doorloopt — en het systeem blijft gewoon antwoorden (K4)
- een coördinatenstelsel verschuift en een zoekopdracht geeft stil nul treffers (K5)
- een veld dat de specificatie voorschrijft, zit niet in de data (K5)
- niemand werkt een onderdeel bij, omdat het geen eigenaar heeft (K2)

Geen van vieren is spectaculair. Alle vier gebeuren, en alle vier zonder foutmelding.

**Wat je checkt:** heb je bij elke faalvorm die je opschrijft een voorbeeld gezien, of bedacht? Bedachte
faalvormen zijn meestal te groot.

---

## Proef 2 · Schrijf het signaal op, niet de diagnose

Vraag 2 gaat mis als je de oorzaak opschrijft. "De index is verouderd" is een diagnose. Het signaal is wat
een gebruiker zegt:

| diagnose (fout hier) | signaal (goed hier) |
|---|---|
| de index is verouderd | "hij noemt een regeling die vorig jaar is vervallen" |
| te dunne index | "hij wordt vaag zodra je iets specifieks vraagt" |
| te streng contract | "hij zegt nooit iets bruikbaars" |
| coördinatenstelsel klopt niet | "dat pand staat op de kaart in de sloot" |

**Wat er onder de motorkap gebeurt.** Je krijgt nooit een diagnose van een gebruiker. Je krijgt een zin
zoals hierboven, en jouw werk is die vertalen. Deze kolom van je beheerkaart is de vertaaltabel.

---

## Proef 3 · De zesde vraag

*Waar neemt het model het denken over?*

Dit is geen technische vraag en er is geen goed antwoord. Wel een verkeerde manier om hem te beantwoorden:
"nergens, het is maar een hulpmiddel". Als dat waar was, zou niemand het gebruiken.

Denk aan waar in jouw proces iemand nu een oordeel velt, en of dat oordeel straks nog gevoed wordt door
alles wat die persoon weet — of alleen nog door wat het systeem toonde.

Uit deze route: het `onzekerheid`-veld staat altijd op waar. Wie daarop zou varen, zou elk antwoord even
serieus nemen en dus geen enkel antwoord. Het oordeel over hoe zeker iets is, ligt nog steeds bij de lezer,
en het systeem doet alsof het dat afneemt.

**Wat je checkt:** wie kijkt er na? En als niemand naar een individueel geval kijkt: wie kijkt er dan naar
het geheel, en hoe vaak?

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De beheerkaart was bijna een architectuurnotitie.** In een eerdere versie van het plan was het
  eindproduct een architectuurdocument. Dat is gewijzigd omdat het niet past bij het dagelijks werk van
  deze doelgroep: een notitie wordt gearchiveerd, een kaart van één A4 wordt gebruikt.
- **Er is nog geen enkele ingevulde kaart.** Het plan rekent zichzelf af op zes bezoekers met een afgeronde
  kaart, waarvan er drie hem in hun eigen team bespreken. Op dit moment staat die teller op nul. Dat is
  geen fout maar het is wel de eerlijke stand.
- **Zonder de maandelijkse tegenspraaksessie verdampt dit.** Dat staat zo in het plan: een ingevulde kaart
  wordt pas een besluit als iemand hem aanvalt. Die sessie is nog niet ingericht.

---

## Wat je hiervan meeneemt

De kaart zelf. **[Vul hem in en download hem](/beheerkaart)** — het is een markdown-bestand, dus je kunt
hem in elke editor openen en in elk document plakken.

Half ingevuld en meegenomen is meer waard dan volledig en blijven liggen.

**Volgende:** de sporen. Spoor W gaat over het Waterlab en een nagebouwd vakinterface; spoor L gaat over
LeefomgevingLab en de chatbot die je in K4 al gebruikt hebt.
