---
id: l02-de-chatbot-van-binnen
titel: "De vergunningen-chatbot van binnen"
spoor: leefomgeving
volgorde: 20
competenties: [B1, B2]
duur_min: 35
beurten: 2
modellen: [klas]
conserven: conserven/l02-de-chatbot-van-binnen.json
status: gepubliceerd
wat_ging_mis: true
bewijs: "de weg van vraag naar antwoord, in zes stappen, voor je eigen toepassing"
poc: leefomgevinglab
routes: ["/chatbot", "/api/chat"]
---

# De vergunningen-chatbot van binnen

In K4 heb je deze chatbot gebruikt om fouten te vinden. Nu kijk je hoe hij werkt — niet als
architectuurplaat, maar als zes stappen die je kunt narekenen.

Het vraagblok onderaan gaat naar dezelfde chatbot; in zijn eigen omgeving staat hij op
**[/chatbot](https://leefomgevinglab.felixisfelix.com/chatbot)**.

**Wat het kost:** 2 modelbeurten.

---

## De zes stappen

Wat er gebeurt tussen jouw vraag en het antwoord op het scherm:

| # | stap | concreet op deze machine |
|---|---|---|
| 1 | jouw vraag wordt omgezet in getallen | `bge-m3`, 1024 getallen |
| 2 | die getallen worden vergeleken met alle opgeslagen stukken | 924 stukken |
| 3 | de vier best passende stukken worden gekozen | `top_k: 4` |
| 4 | die vier gaan mee naar het taalmodel, met een instructie | `Qwen3-8B` |
| 5 | het model schrijft een antwoord dat bij die vier past | |
| 6 | er komt een disclaimer, een vangnet en een bronnenlijst omheen | vaste teksten |

Stap 5 is waar de aandacht altijd naartoe gaat. Stap 2 en 3 bepalen wat er überhaupt te schrijven valt.

---

## Proef 1 · Vier stukken, meer niet

Stel een vraag en kijk naar de bronnenlijst onder het antwoord.

**Kijk naar:** hoeveel bronnen worden er genoemd, en zou het antwoord uit die bronnen te halen zijn?

**Wat er onder de motorkap gebeurt.** De index bevat 924 tekststukken van gemiddeld 1067 tekens, gehaald
uit 170 IPLO-pagina's. Bij elke vraag worden er daarvan **vier** opgehaald. Dat is ongeveer 4.000 tekens
context — minder dan twee A4'tjes.

Alles wat het antwoord daarbuiten beweert, komt uit het model zelf.

**Signaal in je eigen werk:** vraag hoeveel fragmenten er per vraag worden opgehaald. Vier is gebruikelijk.
Het is ook weinig, en het verklaart waarom een chatbot vaak precies één ding goed weet en het volgende
niet.

**Wat je checkt:** `top_k` — zo heet die instelling meestal. Eén getal, en het staat in een
configuratiebestand.

---

## Proef 2 · De rand van de index opzoeken

De index is op 3 september 2026 herbouwd: van 8 fragmenten uit twee webpagina's naar 924 uit 170. Dat is
honderdvijftien keer zoveel.

**Wat je doet:** stel eerst een vraag over vergunningen. Stel daarna een vraag over geluidsniveaus —
bijvoorbeeld wat `Lden` betekent.

**Wat je ziet.** De eerste vraag gaat goed. De tweede levert een vloeiend, zelfverzekerd en fout antwoord.

**Wat er onder de motorkap gebeurt.** IPLO gaat over de Omgevingswet, niet over akoestiek. In alle 924
fragmenten komen de termen `Lden`, `Lmax` en `dB(A)` **nul keer** voor. De vier opgehaalde stukken gaan dan
over geluid in het algemeen, het model schrijft er iets bij uit eigen geheugen, en de bronnenlijst
eronder wijst naar pagina's die het woord niet bevatten.

Dit is een **andere faalvorm** dan een te dunne index, en de remedie is anders: niet meer IPLO-pagina's
toevoegen, maar een andere bron — of de vraag afwijzen.

**Signaal in je eigen werk:** een systeem dat op het ene onderwerp raak is en op het volgende volledig
mis, heeft geen kwaliteitsprobleem maar een bereikprobleem.

**Wat je checkt:** welke bronnen zitten erin, en dekken die het onderwerp waar je naar vraagt? Dat is een
lijst, en die hoort opvraagbaar te zijn.

---

## Proef 3 · Herbouwen verandert de antwoorden

Voor de herbouw kon deze chatbot niets zeggen over externe veiligheid: er was geen enkel fragment over dat
onderwerp. Na de herbouw antwoordt hij op de vraag naar plaatsgebonden risico met de echte grenswaarde:

> "Bij kwetsbare en zeer kwetsbare gebouwen en kwetsbare locaties moet het bevoegde gezag een grenswaarde
> in acht nemen, die maximaal 1 op de miljoen per jaar is."

Dat getal staat in de bron. Vóór 3 september had hetzelfde model op dezelfde vraag iets moeten verzinnen.

**Wat er onder de motorkap gebeurt.** Het model is niet veranderd. De index wel. Dat is het hele verschil
tussen een bruikbaar en een onbruikbaar antwoord — en het is de reden dat "welk model gebruiken jullie"
zelden de nuttigste vraag is.

**Signaal in je eigen werk:** als een systeem opeens beter of slechter antwoordt zonder dat er een nieuw
model is, is er iets aan de index of de bronnen veranderd. Vraag wat, en wanneer.

**Wat je checkt:** wordt bijgehouden wanneer de index herbouwd is en met welke bronnen? Dat is een datum
en een lijst.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De chatbot heette maandenlang iets wat hij niet was.** Er werd over "de vergunningen-chatbot" gesproken
  alsof die de IPLO-documentatie kende. Toen iemand voor het eerst naar de bestandsgrootte van de index
  keek, bleek het 8 fragmenten uit twee webpagina's te zijn — 8.187 tekens in totaal. Niemand had gelogen;
  niemand had gekeken.
- **De herbouw loste het probleem niet op waarvoor hij bedoeld was.** De aanleiding was dat het model
  `Lden` in het verkeerde vakgebied plaatste. Na 924 fragmenten doet het dat nog steeds, want de bron gaat
  er niet over. De aanname "meer bronnen is beter" hield geen stand tegen de vraag "staat het antwoord
  überhaupt in deze bron".
- **Het bouwscript brak af op één pagina.** Bij het ophalen van 100 pagina's zonder pauze ging de bron
  afknijpen, en één mislukking beëindigde de hele run — de andere negenennegentig gingen mee verloren.
  Dezelfde pagina werkte seconden later gewoon. Nu met pauze en herpogingen.
- **De zoekopdracht die moest controleren of `Lden` gedekt was, matchte op `gelden`.** Zeventig van de
  zeventig pagina's scoorden daardoor als "dekt dit begrip". Met woordgrenzen: nul. De conclusie zou
  precies omgekeerd zijn geweest.

---

## Wat je hiervan meeneemt

Teken de zes stappen voor je eigen toepassing:

| # | stap | bij ons is dat | wie beheert het |
|---|---|---|---|
| 1 | vraag omzetten | | |
| 2 | vergelijken met | | |
| 3 | hoeveel stukken opgehaald | | |
| 4 | welk model | | |
| 5 | welke instructie | | |
| 6 | welk contract eromheen | | |

Kun je stap 2 en 3 niet invullen, dan is het waarschijnlijk geen RAG-systeem maar een model dat uit eigen
geheugen praat. Dat is niet erg — het is alleen iets heel anders, en het verjaart sneller.

**Volgende:** module L3 gaat over stap 6: het contract dat om elk antwoord heen zit.
