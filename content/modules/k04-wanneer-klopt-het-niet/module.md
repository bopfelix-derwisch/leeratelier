---
id: k04-wanneer-klopt-het-niet
titel: "Wanneer klopt het antwoord niet?"
spoor: basis
volgorde: 40
competenties: [B2, B3]
duur_min: 35
beurten: 3
modellen: [klas, show]
conserven: conserven/k04.json
status: concept
wat_ging_mis: true
bewijs: "drie zelf gevonden foute antwoorden, elk met faalvorm, signaal en check"
poc: leefomgevinglab
routes: ["/chatbot", "/api/chat", "/kwaliteit"]
---

# Wanneer klopt het antwoord niet?

Je krijgt straks de vraag: *"waarom zegt dat ding dit?"* Dan helpt het niet om te weten hoe een
transformer werkt. Wat helpt is dat je de **vier manieren** herkent waarop een AI-antwoord fout gaat, en
per manier weet welk signaal erbij hoort en wat je dan checkt.

Deze module gebruikt de vergunningen-chatbot van LeefomgevingLab. Die draait op een lokaal taalmodel met
een zoekindex over IPLO- en DSO-documentatie. Hij is niet gebouwd om je te overtuigen; hij is gebouwd om
te laten zien wat er gebeurt.

**Wat je nodig hebt:** je browser. Verder niets.
**Wat het kost:** 3 modelbeurten van je dagbudget.

---

## Wat je gaat zien

Vier faalvormen, elk met een proef die je zelf doet:

| # | Faalvorm | Wat je denkt dat er gebeurt | Wat er werkelijk gebeurt |
|---|---|---|---|
| 1 | **Verouderde kennis** | het antwoord komt uit de bron van vandaag | het komt uit een index die maanden geleden gebouwd is |
| 2 | **Te dunne index** | het systeem kent de hele documentatie | het kent een handvol fragmenten |
| 3 | **Te streng vangnet** | een voorzichtig systeem is een veilig systeem | het onderdrukt informatie die het wél had |
| 4 | **Plausibel maar fout** | het antwoord komt uit de bron | het model vult aan uit eigen geheugen |

Faalvorm 3 is de verrassing. De meeste mensen verwachten alleen fouten in de richting van "te veel
beweren". Onderdrukking is net zo schadelijk en veel moeilijker te zien, want een antwoord dat niets zegt
ziet er nooit fout uit.

---

## Proef 1 · Hoe oud is de kennis?

Stel de chatbot een vraag over een regel of document waarvan je weet dat er dit jaar iets aan veranderd is.

**Kijk naar drie dingen:**
1. Noemt het antwoord een datum of versie? Meestal niet.
2. Verwijst het naar een bron, en zo ja: staat daar een datum bij?
3. Klinkt het even stellig als een antwoord over iets dat wél actueel is?

**Wat er onder de motorkap gebeurt.** De index is één keer gebouwd uit documenten die op dat moment zijn
opgehaald. Daarna verandert hij niet meer, ook niet als de bron verandert. Het model heeft geen enkele
manier om te weten dat zijn fragmenten verouderd zijn — en dus geen enkele reden om te twijfelen.

**Signaal in je eigen werk:** een systeem dat nooit "ik weet niet of dit nog actueel is" zegt, weet dat
inderdaad niet.

**Wat je checkt:** wanneer is de index voor het laatst gebouwd? Dat is één getal en het hoort op een
statuspagina te staan. Staat het er niet, dan is dat je eerste vraag aan de leverancier.

---

## Proef 2 · Hoe veel weet het eigenlijk?

Stel drie vragen die steeds verder van de kern van de documentatie af liggen. Bijvoorbeeld: eerst iets
over een veelbesproken onderwerp, dan iets over een randgeval, dan iets over een detail dat vrijwel zeker
niet in de opgehaalde documenten staat.

**Kijk naar:** waar het antwoord van karakter verandert. Er is een grens waarboven het systeem vaag wordt,
of juist opeens heel algemeen. Die grens is de rand van de index.

**Wat er onder de motorkap gebeurt.** De zoekindex bestaat uit stukken tekst — chunks — met bijbehorende
getallenreeksen. Bij een vraag worden de best passende stukken opgehaald en aan het model meegegeven. Zit
het antwoord niet in die stukken, dan valt het model terug op wat het uit zijn training denkt te weten.

Op deze machine is die index **klein**. Hoe klein precies staat in het inspectierapport bij deze module.
Dat is geen schande — het is een proefopstelling — maar het verandert wel wat je van het antwoord mag
verwachten.

**Signaal in je eigen werk:** vraag niet "hoe goed is de chatbot", vraag "hoeveel zit erin". Het aantal
documenten in de index zegt meer over de bruikbaarheid dan welke demo dan ook.

**Wat je checkt:** hoeveel documenten of fragmenten zitten er in, en welke bronnen zijn dat. Beide horen
opvraagbaar te zijn.

---

## Proef 3 · Wanneer is voorzichtig te voorzichtig?

Stel een vraag waarvan je zeker weet dat het antwoord in de documentatie staat, maar formuleer hem alsof
je om een oordeel vraagt. Bijvoorbeeld: niet *"wat staat er over X"* maar *"mag ik X"*.

**Kijk naar:** krijg je de informatie die er wél is, of krijg je vooral een disclaimer?

**Wat er onder de motorkap gebeurt.** Dit systeem heeft bewust een conservatief antwoordcontract:
disclaimer, vangnet, geen stellige uitspraken. Dat is een verstandige eis — maar de bouwers noteerden er
zelf bij dat het contract niet zó streng mag zijn dat het nuttige, gevonden informatie onderdrukt. Dat is
een reële spanning en er bestaat geen instelling die hem oplost.

**Signaal in je eigen werk:** gebruikers die zeggen "hij zegt nooit iets nuttigs" melden meestal geen
kapot systeem maar een te streng contract. Dat is een instelbaar probleem, geen technisch defect — maar
alleen als iemand doorheeft dat dat de oorzaak is.

**Wat je checkt:** is er een geschreven antwoordcontract, en wie mag het wijzigen? Als niemand weet waar
het staat, is het waarschijnlijk in een prompt terechtgekomen die niemand beheert.

---

## Proef 4 · Klopt de bron die het noemt?

Vraag om een antwoord mét bronverwijzing. Probeer dan de genoemde bron te vinden.

**Kijk naar:** verwijst het naar iets specifieks en controleerbaars, of naar iets dat plausibel klinkt maar
niet aanwijsbaar is?

**Wat er onder de motorkap gebeurt.** Een taalmodel produceert tekst die past bij de vraag. Een
bronverwijzing is óók tekst. Zonder een expliciete koppeling tussen antwoord en het daadwerkelijk
opgehaalde fragment is er geen enkele garantie dat de genoemde bron bestaat.

**Signaal in je eigen werk:** verwijzingen die er goed uitzien maar niet aanklikbaar zijn. Als je een
bronvermelding niet in twee klikken kunt controleren, is ze niet meer waard dan de rest van de zin.

**Wat je checkt:** komt de bronverwijzing uit het opgehaalde fragment of uit de gegenereerde tekst? Dat is
een van de scherpste vragen die je aan een bouwer kunt stellen.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De index staat stil sinds juni.** Hij is één keer gebouwd en daarna niet meer aangeraakt, terwijl de
  bronnen wel doorliepen. Niemand merkte dat, omdat de chatbot bleef antwoorden. Een systeem dat stilstaat
  ziet er precies hetzelfde uit als een systeem dat werkt.
- **De index bleek een orde van grootte kleiner dan iedereen aannam.** Bij het opzetten van dit atelier
  werd de bestandsgrootte pas echt bekeken. Tot dat moment werd er over "de vergunningen-chatbot" gepraat
  alsof die de IPLO-documentatie kende.
- **Het antwoordcontract sloeg door.** De ontwerpers legden het zelf vast: een conservatief contract is een
  harde eis, maar het mag nuttige gevonden informatie niet onderdrukken. Dat evenwicht is meerdere keren
  bijgesteld en is nog steeds niet af.
- **Gegokte endpoints klopten zelden.** Een terugkerende les uit de kwaliteitspagina: geraden endpoints,
  headers en veldnamen kloppen bijna nooit. De OpenAPI-specificatie plus één echte aanroep zijn nodig
  vóór er gebouwd wordt — niet erna.

---

## Wat je hiervan meeneemt

Vier faalvormen, vier signalen, vier checks. Zet ze straks op je beheerkaart:

| Faalvorm | Signaal | Check |
|---|---|---|
| Verouderde kennis | nooit twijfel over actualiteit | wanneer is de index gebouwd? |
| Te dunne index | vaag worden bij randvragen | hoeveel fragmenten, welke bronnen? |
| Te streng vangnet | "hij zegt nooit iets nuttigs" | waar staat het antwoordcontract, wie beheert het? |
| Plausibel maar fout | onaanklikbare bronvermelding | komt de bron uit het fragment of uit de tekst? |

**Volgende:** module K5 laat zien wat er gebeurt als de bron zelf verandert. Die kost geen modelbeurten.
