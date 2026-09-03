---
id: w02-toen-het-misging
titel: "Toen het misging — randvoorwaarden en ontbrekende data"
spoor: waterlab
volgorde: 20
competenties: [B3]
duur_min: 30
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de niet-fysische stappen in je eigen keten benoemd"
poc: waterlab
routes: ["/api/validation", "/api/timeseries/{station}"]
---

# Toen het misging

Een hydrologisch model draait pas als elke randvoorwaarde ergens vandaan komt. En bij het naspelen van
oude gebeurtenissen blijkt telkens hetzelfde: **de data die je nodig hebt, bestaat niet altijd.**

Deze module gaat over wat je dan doet, en vooral over hoe je opschrijft wat je gedaan hebt.

Deze module kost **geen modelbeurten**.

---

## Proef 1 · De instroom die er niet was

Het Waterlab speelt het hoogwater van januari 1995 na. Daarvoor is nodig: hoeveel water er bij Westervoort
de IJssel in stroomt, per dag, in die weken.

**Die meting bestaat niet.** Vóór 2000 is er geen bruikbare reeks.

**Wat er gedaan is.** De instroom is **gesynthetiseerd** uit het RIZA-archief: afgeleid uit andere
gegevens, niet gemeten. En op het dashboard staat dat er letterlijk bij, als een markering dat deze stap
*niet fysisch* is.

**Waarom dat het interessante deel is.** Niet dat er gesynthetiseerd moest worden — dat is normaal en vaak
onvermijdelijk. Het interessante is dat het **in de keten zichtbaar gemaakt** is, op de plek waar iemand
het resultaat leest. Niet in een bijlage, niet in een readme.

**Signaal in je eigen werk:** ergens in jouw keten zit een stap die afgeleid, geïnterpoleerd, geschat of
overgenomen is. Meestal meer dan één. De vraag is niet of ze er zijn, maar of ze gemarkeerd zijn op de
plek waar de uitkomst gelezen wordt.

**Wat je checkt:** neem een cijfer dat jouw organisatie publiceert. Kun je van elke tussenstap zeggen of hij
gemeten of afgeleid is? En ziet de lezer dat ook?

---

## Proef 2 · Een randvoorwaarde bepaalt de uitkomst

Bij het naspelen van 1995 komt de piekafvoer bij Kampen uit op ongeveer **849 m³/s**.

**Wat er onder de motorkap gebeurt.** Dat getal wordt niet bepaald door de neerslag of het model, maar
door de instroom bij Westervoort — de randvoorwaarde die, zoals je in proef 1 zag, gesynthetiseerd is.

De kwaliteit van de uitkomst hangt dus af van een reeks die niet gemeten is. Dat maakt het resultaat niet
waardeloos, maar het bepaalt wel wat je ermee mag doen: het is bruikbaar om gedrag te bestuderen, niet om
een getal uit te citeren.

**Signaal in je eigen werk:** een uitkomst die overtuigend precies is — 849, niet "ongeveer 850" — terwijl
de invoer een schatting was. Precisie in de uitvoer zegt niets over de invoer.

**Wat je checkt:** welke invoer bepaalt het eindresultaat het sterkst, en hoe zeker is juist die?

---

## Proef 3 · Wat er stukging in het model zelf

Bij het opzetten zijn er problemen tegengekomen die niets met water te maken hebben. Ze zijn gedocumenteerd,
inclusief aanbevelingen aan de bouwers van het modelpakket:

- **Een toestandsbestand met de verkeerde dimensies.** Het model verwacht een variabele met drie of vier
  dimensies; er werd er een met twee aangeboden. De foutmelding zei niet welke dimensie ontbrak. De
  aanbeveling die het team opschreef: laat de foutmelding vertellen wat er verwacht werd.
- **Een bestand dat alleen bestond om een controle te passeren.** Bij een koude start leest het model het
  toestandsbestand helemaal niet — maar het controleert wel of het er is. Er is toen een symlink gelegd
  naar het bestand van een ander jaar, puur om die controle te doorstaan.
- **Ontbrekende waarden op actieve cellen aan de rand van het gebied.** De forceringsdata had gaten precies
  daar waar het model ze wel nodig had.

**Wat er onder de motorkap gebeurt.** Geen van deze drie gaat over hydrologie. Het zijn contractproblemen:
wat verwacht het ene onderdeel van het andere, en wat gebeurt er als dat net niet klopt.

**Signaal in je eigen werk:** dit is het soort probleem dat in een projectverslag verdwijnt onder
"technische uitdagingen". Het zijn juist de dingen die de volgende ploeg opnieuw tegenkomt.

**Wat je checkt:** wordt er opgeschreven wat er misging én wat de aanbeveling was? En gaat die aanbeveling
terug naar wie het kan oplossen?

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **Een symlink om een controle te passeren.** Het model controleert of een toestandsbestand bestaat, maar
  leest het bij een koude start niet. De oplossing was een verwijzing naar het bestand van een ander jaar.
  Het werkt, het is opgeschreven, en het is precies het soort constructie dat over twee jaar niemand meer
  begrijpt.
- **De foutmelding hielp niet.** Er ging een halve dag in zitten voordat duidelijk was welke dimensie
  ontbrak. Dat is geen fout van de gebruiker.
- **De 1995-instroom en de 2021-instroom zijn niet vergelijkbaar** — het ene jaar gesynthetiseerd, het
  andere gemeten, en de simulatieperiodes verschillen. Wie de piekgetallen naast elkaar legt zonder dat te
  weten, trekt een conclusie die nergens op slaat.

---

## Wat je hiervan meeneemt

| vraag over je eigen keten | jouw antwoord |
|---|---|
| Welke stappen zijn afgeleid of geschat in plaats van gemeten? | |
| Staat dat gemarkeerd waar de uitkomst gelezen wordt? | |
| Welke invoer bepaalt de uitkomst het sterkst? | |
| Zijn er constructies die alleen bestaan om een controle te passeren? | |

De laatste vraag levert bij elke keten iets op. Ze zijn niet fout; ze zijn onzichtbaar.

**Volgende:** module W3 zet drie casussen naast elkaar en laat zien wat validatie wel en niet bewijst.
