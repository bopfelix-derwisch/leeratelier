---
id: k00-proefmodule
titel: "Proefmodule - werkt de keten?"
spoor: basis
volgorde: 0
competenties: []
duur_min: 5
beurten: 1
modellen: [klas]
conserven: conserven/k00-proefmodule.json
status: gepubliceerd
wat_ging_mis: true
bewijs: "een antwoord met een zichtbaar bronlabel"
poc: geen
routes: []
---

# Proefmodule

Deze module bestaat om de keten te bewijzen, niet om iets te onderwijzen. Ze wordt
vervangen zodra K1 en K4 gepubliceerd zijn.

Wat je hier doet: één vraag stellen en kijken wat er onder het antwoord staat.

## Wat je gaat zien

| onderdeel | waar je op let |
|---|---|
| De budgetmeter rechtsboven | die telt af zodra je een vraag stelt |
| Het bronlabel onder het antwoord | cache, klasmodel, showmodel of conserf |
| De leeftijd van de zoekindex | staat erbij, ook als niemand ernaar vraagt |
| De banner bovenaan | verschijnt zodra er iets weg is |

## De proef

Stel hieronder een willekeurige vraag. Kijk daarna naar drie dingen.

**Ten eerste: waar komt dit antwoord vandaan?** Onder elk antwoord staat het. Een
atelier dat leert antwoorden te wantrouwen, mag zelf niet verzwijgen waar een antwoord
vandaan komt.

**Ten tweede: wat kostte het?** De meter bovenaan telt af. Modules die nul beurten
kosten staan als zodanig gemarkeerd in de route.

**Ten derde: stel dezelfde vraag nog een keer.** Het antwoord komt dan uit de cache,
kost geen beurt, en het label zegt dat. Dat is geen truc maar de reden dat het
dagbudget haalbaar is: in een atelier stelt iedereen ongeveer dezelfde vragen.

## Wat hier misging

Tijdens het bouwen van deze keten stond in de opslaglaag een docstring die beschreef
dat elke aanroeper een eigen databaseverbinding krijgt. De code deelde er een. Dat
werkte in elke test met een gebruiker en viel om zodra er meerdere tegelijk waren --
precies waarvoor die laag bestaat.

Vlak daarna bleek de budgetafboeking niet bestand tegen gelijktijdigheid: twee
verzoeken lazen dezelfde stand voordat een van beide had geschreven, waardoor een
afboeking verdween. Beide fouten waren onzichtbaar bij een enkele bezoeker.

De les is niet dat er fouten in zaten. De les is dat je het verschil tussen de
beschrijving en het gedrag alleen ziet als je het onder belasting meet.

## Wat je meeneemt

Dat een antwoord altijd een herkomst heeft, en dat een systeem dat die herkomst niet
toont, iets voor je verbergt -- ook als het dat niet expres doet.

## En verder

Deze proefmodule verdwijnt zodra de echte route staat. Ga daarna verder met K1, de
rondgang over de machine.
