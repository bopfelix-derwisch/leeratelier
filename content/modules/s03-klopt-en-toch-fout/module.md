---
id: s03-klopt-en-toch-fout
titel: "Een antwoord dat klopt en toch fout is"
spoor: sturing
volgorde: 30
competenties: [S2, S3]
duur_min: 25
beurten: 2
modellen: [klas, poc]
conserven: s03-klopt-en-toch-fout
status: gepubliceerd
wat_ging_mis: true
bewijs: "drie manieren benoemd waarop een antwoord fout kan zijn zonder dat je het ziet"
poc: leefomgevinglab
routes: []
---

# Een antwoord dat klopt en toch fout is

Dit is de enige module van deze route waarin je zelf een vraag stelt. Hij kost **twee modelbeurten**,
die vooraf voor je zijn gereserveerd.

Het doel is niet dat je leert een systeem te repareren. Het doel is dat je één keer zelf meemaakt hoe een
fout antwoord eruitziet, zodat je weet wat je níét kunt zien.

---

## Drie manieren waarop het misgaat

Er zijn er meer, maar deze drie komen op deze machine werkelijk voor en zijn genoeg om mee te beginnen.

**1. Het model kent het woord uit een ander vakgebied.**
Iemand vroeg dit lab wat "plaatsgebonden risico" is — een term uit de externe veiligheid, over de kans
dat iemand op een bepaalde plek overlijdt door een ongeval met gevaarlijke stoffen. Het kale model gaf
een keurig, vloeiend antwoord over **beleggingsrisico**. Niet half fout: volledig het verkeerde
vakgebied, in onberispelijke zinnen.

Met de zoekindex erbij gaf hetzelfde systeem het juiste antwoord, met artikel 5.6 van het Besluit
kwaliteit leefomgeving en drie bronvermeldingen.

**2. De bron is verouderd.**
De index is een kopie van de documenten, gemaakt op een moment in het verleden. Verandert de regel, dan
verandert het antwoord niet mee. Het systeem meldt dat niet, want het weet het niet.

**3. De vraag valt buiten wat de bron behandelt.**
Dit is de verraderlijkste. Een vraag over geluidbelasting in Lden liet zich hier niet beantwoorden — niet
omdat de index te klein was, maar omdat de gebruikte bron dat onderwerp simpelweg niet dekt. Het systeem
gaf toch antwoord. Een systeem dat zwijgt over wat het niet dekt, is niet stil; het is stellig.

---

## Proef · Stel er zelf een

Stel hieronder een vraag over een onderwerp waar je **zelf verstand van heeft**. Dat is essentieel: bij
een onderwerp dat je niet kent, kun je het verschil tussen goed en fout niet zien, en dan leert de proef
je niets.

Kies bij voorkeur iets uit je eigen vakgebied waarvan je weet dat er onlangs iets aan is veranderd.

**Kijk daarna naar drie dingen, in deze volgorde:**

1. **Staat er een bron onder?** En zo ja, is dat een echte vindplaats of een vage verwijzing?
2. **Staat er een datum of versie bij?** Vrijwel nooit. Vraag je dan af hoe oud dit antwoord is.
3. **Klinkt het even stellig als een antwoord waarvan je wél zeker weet dat het klopt?** Vergelijk de
   toon. Er zit geen verschil in. Dat is precies het probleem.

Onder elk antwoord staat waar het vandaan kwam: live van een model, live uit de POC met zoekindex, of
voorberekend. Let daar op, want dat verschil verklaart vaak het verschil in kwaliteit.

---

## Wat dit voor je besluit betekent

Je hoeft geen van deze fouten zelf te kunnen repareren. Je moet ze kunnen **verwachten**, en dat vertaalt
zich in drie concrete eisen die je kunt stellen voordat je tekent:

- Elk antwoord toont zijn bron, en die bron is aanklikbaar.
- Ergens staat zichtbaar wanneer de index voor het laatst is ververst.
- Er is opgeschreven wat het systeem **niet** dekt, en het zegt dat ook als je ernaar vraagt.

Deze drie zijn technisch niet moeilijk. Dat ze zo vaak ontbreken, komt doordat niemand erom vraagt.

---

## Wat hier misging

In dit atelier zelf, een week lang: het vraagvenster in het portaal ging **langs de zoekindex heen**.
Vragen gingen rechtstreeks naar het kale taalmodel, terwijl de modules eromheen juist over die
ophaalstap gingen.

Het gevolg was het voorbeeld hierboven: op "wat is het plaatsgebonden risico" antwoordde het atelier
zelf iets over beleggingsrisico. De module beloofde intussen proeven over indexleeftijd, indexomvang en
bronvermelding die geen van drieën konden werken, want er wás geen index in de weg.

Niemand had het gemerkt. Het is gevonden door een vraag die niets met techniek te maken had: *wanneer
zijn er eigenlijk links nodig?* Bij het nalopen van de verwijzingen bleek dat een module naar een chatbot
verwees die de bezoeker via het portaal helemaal niet gebruikte.

Onthoud dat mechanisme. **De ernstigste fouten zitten niet in een onderdeel, maar in de aansluiting
tussen twee onderdelen die elk afzonderlijk prima werken.** Een keten waarvan elke schakel is getest,
is niet hetzelfde als een geteste keten. Vraag bij een oplevering dus niet alleen of de onderdelen zijn
getest, maar of iemand de hele weg van vraag tot antwoord één keer heeft nagelopen.
