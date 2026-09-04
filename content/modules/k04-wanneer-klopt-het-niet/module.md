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
status: gepubliceerd
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
een zoekindex over IPLO-documentatie. Hij is niet gebouwd om je te overtuigen; hij is gebouwd om te laten
zien wat er gebeurt.

Het vraagblok onderaan deze pagina stuurt je vraag naar diezelfde chatbot, dus mét de zoekindex ertussen.
Onder elk antwoord zie je welke bronnen hij meegaf en wat er in zijn antwoordcontract stond. Wil je hem in
zijn eigen omgeving zien, dan staat hij op **[de chatbot van LeefomgevingLab](https://leefomgevinglab.felixisfelix.com/chatbot)**.

**Wat je nodig hebt:** je browser. Verder niets.
**Wat het kost:** 3 modelbeurten van je dagbudget.

---

## Wat je gaat zien

Vijf faalvormen, elk met een proef die je zelf doet:

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

Op deze machine is die index op 3 september 2026 opnieuw gebouwd: van **8 fragmenten uit twee
webpagina's** naar **924 fragmenten uit 170 pagina's**. Dat is honderdvijftien keer zoveel, en het is te
merken — een vraag over plaatsgebonden risico levert nu de echte grenswaarde uit de bron op, waar eerder
geen enkel fragment over dat onderwerp bestond.

**Maar er is een tweede rand, en die is verraderlijker.** IPLO gaat over de Omgevingswet, niet over
akoestiek. De termen `Lden`, `Lmax` en `dB(A)` komen in die 924 fragmenten **nul keer** voor. Een vraag
over geluidsniveaus valt dus buiten het bronbereik, hoe groot de index ook wordt. Voor jou als gebruiker
ziet dat er identiek uit als een te dunne index — vloeiend, zelfverzekerd, fout — maar de remedie is een
andere: niet vergroten, maar een andere bron toevoegen of de vraag afwijzen.

Dat onderscheid is de kern van deze proef:

| wat je ziet | wat het is | wat je eraan doet |
|---|---|---|
| overal vage antwoorden | te dunne index | index vergroten |
| raak op één onderwerp, mis op het volgende | buiten het bronbereik | andere bron, of de vraag afwijzen |

**Signaal in je eigen werk:** vraag niet "hoe goed is de chatbot", vraag "hoeveel zit erin". Het aantal
documenten in de index zegt meer over de bruikbaarheid dan welke demo dan ook.

**Wat je checkt:** hoeveel documenten of fragmenten zitten er in, en welke bronnen zijn dat. Beide horen
opvraagbaar te zijn.

---

## Proef 3 · Wanneer is voorzichtig te voorzichtig?

Stel een vraag waarvan je zeker weet dat het antwoord in de documentatie staat, maar formuleer hem alsof
je om een oordeel vraagt. Bijvoorbeeld: niet *"wat staat er over X"* maar *"mag ik X"*.

**Kijk naar:** krijg je de informatie die er wél is, of krijg je vooral een disclaimer?

**Wat er onder de motorkap gebeurt.** Dit systeem heeft een conservatief antwoordcontract: elk antwoord
draagt een disclaimer, een vangnet dat naar het bevoegd gezag verwijst, en een veld `onzekerheid`.

Kijk naar dat laatste veld. In de broncode staat het op vier plaatsen, en overal als vaste waarde:

```python
{"vraag": activiteit, "bron": BRON, "onzekerheid": True, ...}
```

**`onzekerheid` wordt nergens berekend.** Het staat altijd op waar, of het antwoord nu woordelijk uit een
opgehaald fragment komt of volledig uit het geheugen van het model. Een signaal dat altijd afgaat, draagt
geen informatie.

Dat is geen slordigheid maar een reële spanning: een systeem dat zijn eigen zekerheid moet inschatten,
moet weten wanneer het iets niet weet — en dat is precies wat een taalmodel niet kan.

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

**Wat hier op deze machine gebeurde, op 3 september 2026.** Gevraagd wat `Lden` betekent, antwoordde de
chatbot dat het staat voor *"Lärmpegel Dauer nacht"*. Die uitschrijving bestaat niet; Lden is
*level day-evening-night*. En eronder stonden vier IPLO-bronnen als onderbouwing, waaronder
`iplo.nl/thema/geluid/geluid-regelgeving/geluidproductieplafond/`.

In geen van die vier pagina's komt het woord Lden voor.

Het ophaalmechanisme leverde de dichtstbijzijnde fragmenten over geluid in het algemeen, het model schreef
het antwoord uit eigen geheugen, en de bronnenlijst eronder gaf dat verzinsel het aanzien van iets dat
nagezocht was. Het vangnet werkte daarbij gewoon: `onzekerheid: true`, disclaimer, verwijzing naar het
bevoegd gezag. En toch een zelfverzekerd fout antwoord met vier links eronder.

**Een bronvermelding bewijst niet dat het antwoord uit die bron komt.** Dat is de scherpste les van deze
hele module.

**Signaal in je eigen werk:** verwijzingen die er goed uitzien maar niet aanklikbaar zijn. Als je een
bronvermelding niet in twee klikken kunt controleren, is ze niet meer waard dan de rest van de zin.

**Wat je checkt:** komt de bronverwijzing uit het opgehaalde fragment of uit de gegenereerde tekst? Dat is
een van de scherpste vragen die je aan een bouwer kunt stellen.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De index stond 74 dagen stil, en niemand merkte het.** Gebouwd op 21 juni, daarna niet meer
  aangeraakt terwijl de bronnen doorliepen. De chatbot bleef gewoon antwoorden. Een systeem dat stilstaat
  ziet er precies hetzelfde uit als een systeem dat werkt — dat is de hele reden dat index-leeftijd op een
  statuspagina hoort. Sinds 3 september staat die leeftijd onder elk antwoord in dit atelier.
- **De index was een orde van grootte kleiner dan iedereen aannam. Twee ordes, eigenlijk.** Er werd over
  "de vergunningen-chatbot" gesproken alsof die de IPLO-documentatie kende. Toen iemand voor het eerst naar
  de bestandsgrootte keek, bleek het **8 fragmenten uit twee webpagina's** te zijn, samen 8.187 tekens.
  Niemand had gelogen; niemand had gekeken.
- **Het `onzekerheid`-veld is een vaste waarde.** Elk antwoord meldt onzekerheid, ook een antwoord dat
  woordelijk uit een opgehaald fragment komt. In de broncode staat het op vier plaatsen als letterlijke
  `True` en het wordt nergens berekend. Een waarschuwing die altijd afgaat, is geen waarschuwing.
- **Een gegokt endpoint bestond niet.** Van de kwaliteitspagina van LeefomgevingLab zelf: *"Het gegokte
  operatie-pad bestond niet; de echte is `werkzaamheden/_bepaalRegelbeheerobjectTyperingen` (POST)."* De
  les die daar als terugkerend patroon staat genoteerd: *"Gegokte endpoints, headers en veldnamen kloppen
  zelden; de OpenAPI-spec plus een live call zijn nodig vóór het bouwen."*
- **De herbouw loste het probleem niet op waarvoor hij bedoeld was.** De index werd vergroot omdat het
  model `Lden` in het verkeerde vakgebied plaatste. Na 924 fragmenten doet het dat nog steeds, want IPLO
  gaat niet over akoestiek. De aanname "meer bronnen is beter" hield geen stand tegen de vraag "staat het
  antwoord überhaupt in deze bron".

---

## Wat je hiervan meeneemt

Vijf faalvormen, vijf signalen, vijf checks. Zet ze straks op je beheerkaart:

| Faalvorm | Signaal | Check |
|---|---|---|
| Verouderde kennis | nooit twijfel over actualiteit | wanneer is de index gebouwd? |
| Te dunne index | overal vaag worden | hoeveel fragmenten, welke bronnen? |
| Buiten het bronbereik | raak op het ene onderwerp, mis op het volgende | staat dit onderwerp überhaupt in de bron? |
| Te streng vangnet | "hij zegt nooit iets nuttigs" | wordt het onzekerheidssignaal berekend of staat het vast? |
| Plausibel maar fout | bronvermelding die je niet kunt narekenen | komt de bron uit het fragment of uit de tekst? |

Het zijn er vijf geworden in plaats van vier. De vijfde — buiten het bronbereik — kwam boven bij het
vergroten van de index, en is de moeilijkste: hij ziet er precies uit als de tweede.

**Volgende:** module K5 laat zien wat er gebeurt als de bron zelf verandert. Die kost geen modelbeurten.
