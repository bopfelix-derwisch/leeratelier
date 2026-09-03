---
id: k06-draaiend-houden
titel: "Draaiend houden — en wie er belt"
spoor: basis
volgorde: 60
competenties: [B4]
duur_min: 25
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de beheerlast van je eigen toepassing, in uren en in namen"
poc: sysmonitor
routes: []
---

# Draaiend houden

Een AI-toepassing bouwen is een project. Hem draaiend houden is een dienstverband. Deze module gaat over
het tweede, want daar zit het meeste van de kosten en vrijwel alle verrassingen.

Deze module kost **geen modelbeurten**.

---

## Wat je gaat zien

Zes signalen die op deze machine bewaakt worden, met per signaal wat er gebeurt als hij afgaat:

| signaal | let op | alarm | wat je dan doet |
|---|---:|---:|---|
| klasmodel niet actief | — | meteen | de unit herstarten; tot dan gaat alles naar het trage model |
| dagbudget verbruikt | 70 % | 90 % | alles standaard naar het snelle model |
| wachtrij te diep | 4 | 8 | nieuwe vragen krijgen een voorberekend antwoord |
| antwoorden te traag | 60 s | 120 s | het trage model uit de route halen |
| zoekindex verouderd | 30 d | 90 d | herbouwen — duurt drie minuten |
| bezoekers vastgelopen | 3 | 10 | de meldingen lezen |

Let op de laatste rij. Vijf van de zes signalen gaan over techniek; de zesde gaat over mensen, en die is
de enige die niet vanzelf overgaat.

---

## Proef 1 · Een drempel is een besluit, geen natuurwet

Kijk naar de drempel voor "antwoorden te traag": 60 seconden let op, 120 seconden alarm.

**Waar komen die getallen vandaan?** Uit het plan, geschreven voordat er iets gemeten was. Toen er later
wel gemeten werd, bleek: bij vier gelijktijdige bezoekers is het traagste antwoord 49 seconden, bij acht
is het 86. De let-op-drempel gaat dus precies af tussen vier en acht bezoekers — waar het ongemakkelijk
begint te worden.

Dat was geluk, geen ontwerp. Maar het is wel controleerbaar geluk: er is een meting waarmee je de drempel
kunt verdedigen of bijstellen.

**Signaal in je eigen werk:** vraag bij elke drempel waar het getal vandaan komt. "Dat stond er al" is het
meest voorkomende antwoord en het minst bruikbare.

**Wat je checkt:** is er van elke alarmdrempel een meting die hem rechtvaardigt? Zo niet, dan gaat het
alarm ofwel te vaak af — waarna niemand meer kijkt — ofwel nooit.

---

## Proef 2 · Wat een goed alarm zegt

De monitoring op deze machine geeft bij elk alarm een concreet commando. Niet "onderzoek dit nader", maar
bijvoorbeeld:

> *Zoekindex verouderd — herbouwen met `python3 scripts/07_build_rag_index.py` (duurt circa 3 minuten).
> Niet tijdens openingstijd: K4 en spoor L worden er onvoorspelbaar van.*

Drie dingen zitten daarin: wat je doet, hoe lang het duurt, en wanneer je het niet moet doen.

**Wat er onder de motorkap gebeurt.** Dat laatste zinnetje is het belangrijkst en het minst
vanzelfsprekend. Een index herbouwen tijdens gebruik betekent dat twee bezoekers dezelfde vraag stellen en
verschillende antwoorden krijgen, zonder dat iemand weet waarom.

**Signaal in je eigen werk:** een alarm dat je niet vertelt wat te doen, is een alarm waarvoor je iemand
moet bellen die het wel weet. Dat is de duurste vorm van monitoring die er is.

**Wat je checkt:** neem het laatste alarm dat jullie systeem gaf. Stond erin wat je moest doen? Kon degene
die piepte dat ook echt doen?

---

## Proef 3 · Wie belt er, en wanneer

Dit atelier staat permanent open en wordt beheerd door één persoon die niet altijd bereikbaar is. Dat is
geen slordigheid maar een keuze, en er hoort een ontwerp bij:

- alle diensten herstarten zichzelf, onbeperkt
- valt een model weg, dan schakelt het systeem naar het andere
- vallen beide weg, dan komen antwoorden uit een voorberekende voorraad
- het dagbudget reset vanzelf om middernacht, zonder taak die kan mislukken
- op de inlogpagina staat: *dit is een privé-lab van één persoon; storingen kunnen dagen duren*

Die laatste regel is het goedkoopste beheersinstrument dat er bestaat. Verwachtingen die kloppen kosten
niets; verwachtingen die niet kloppen kosten vertrouwen.

**Signaal in je eigen werk:** vraag wie er 's nachts belt als de AI-toepassing eruit ligt. Als het antwoord
"niemand, dan wachten we tot morgen" is, is dat prima — mits het ook zo op het scherm staat.

**Wat je checkt:** staat de reactietermijn ergens waar de gebruiker hem ziet, of alleen in een contract dat
de gebruiker nooit leest?

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De monitoringdienst zelf stond niet onder versiebeheer.** Uitgerekend de dienst die alle storingen moet
  melden, had geen geschiedenis en geen weg terug. Rechtgezet op 3 september 2026.
- **De index stond 74 dagen stil zonder dat iemand het merkte.** Er was geen drempel voor index-leeftijd,
  dus er ging niets af. Die drempel bestaat nu — maar hij bestaat omdat het al een keer was misgegaan, niet
  omdat iemand het vooraf bedacht.
- **De storingsbanner had zelf een storing kunnen krijgen.** De monitor schrijft een bestandje dat het
  portaal toont. Zou de monitor stilvallen, dan bleef de laatste melding staan alsof hij actueel was. Nu
  wordt een melding ouder dan 90 minuten genegeerd. Een waarschuwing die niemand meer bijwerkt, is
  gevaarlijker dan geen waarschuwing.
- **Er is nog steeds maar één beheerder.** Dit staat als openstaand risico in het besluitenlog en is niet
  opgelost. Twee opties: een tweede persoon met toegang, of de verwachting expliciet verlagen. Allebei
  overslaan is het risico, en dat is precies wat er nu gebeurt.

---

## Wat je hiervan meeneemt

Voor de beheerkaart, in uren en in namen:

| vraag | jouw antwoord |
|---|---|
| Hoeveel uur per maand kost het bijhouden van de bron of index? | |
| Wie doet dat, en wat gebeurt er als die persoon weg is? | |
| Welke alarmen bestaan er, en waar komen de drempels vandaan? | |
| Wie belt er buiten kantooruren, en staat dat ergens waar de gebruiker het ziet? | |
| Wat is de laatste keer dat iemand een alarm heeft nagelopen? | |

De laatste vraag is de scherpste. Monitoring waar niemand naar kijkt is duurder dan geen monitoring, want
hij wekt de indruk dat er iemand kijkt.

**Volgende:** module K7, waar je de kaart invult en meeneemt.
