---
id: w01-een-vakinterface-nabouwen
titel: "Een vakinterface nabouwen — prikkelend en gevaarlijk"
spoor: waterlab
volgorde: 10
competenties: [B2, B6]
duur_min: 30
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de vraag geformuleerd die je stelt als iets eruitziet als een dienst"
poc: waterlab
routes: ["/fews/rest/fewspiservice/v1/filters", "/fews/rest/fewspiservice/v1/locations"]
---

# Een vakinterface nabouwen

In het Waterlab draait een emulatie van de PI-REST-service van Delft-FEWS: het systeem waarmee
waterschappen en Rijkswaterstaat hun tijdreeksen uitwisselen.

Nagebouwd, op een proefopstelling, op één machine in een woonkamer. En het werkt: een echte
FEWS-client die op dit adres wordt gezet, praat er gewoon mee.

Deze module gaat over waarom dat prikkelend is en waarom het gevaarlijk is, en die twee zijn niet los
verkrijgbaar.

Deze module kost **geen modelbeurten**.

---

> ## Lees dit eerst
>
> **Dit is geen operationele dienst.** De data komen uit een proefopstelling met een hydrologisch model dat
> op deze machine draait. Er hangt geen beheerorganisatie achter, geen dienstverleningsovereenkomst, geen
> wachtdienst. Gebruik hier niets van voor een beslissing die iemand raakt.
>
> Deze waarschuwing staat hier en niet in een voetnoot, omdat een emulatie die goed genoeg is om mee te
> praten, ook goed genoeg is om verkeerd begrepen te worden.

---

## Wat je gaat zien

Open `/fews/rest/fewspiservice/v1/locations`. Je krijgt dit terug:

```json
{"locations":[
  {"locationId":"KAMPEN","shortName":"Kampen","lon":5.921,"lat":52.555},
  {"locationId":"WESTERVOORT","shortName":"Westervoort","lon":5.969,"lat":51.964},
  {"locationId":"LOBITH","shortName":"Lobith","lon":6.115,"lat":51.866}
]}
```

Drie echte meetlocaties op de IJssel en de Rijn, in het formaat dat de PI-service voorschrijft, op het pad
dat de PI-service voorschrijft.

Er is aan dit antwoord niets te zien dat verraadt dat het een proefopstelling is.

---

## Proef 1 · Waarom dit prikkelt

**Wat je doet:** vraag de filters op via `/fews/rest/fewspiservice/v1/filters`.

**Wat er onder de motorkap gebeurt.** Door het bestaande contract van een vakinterface na te bouwen, werkt
alle software die dat contract al kent — zonder aanpassing. Dat is een reëel en waardevol patroon: je hoeft
geen nieuwe koppeling te bouwen, geen client te overtuigen, geen standaard te bevechten.

Voor een proefopstelling is dat goud. Je kunt een idee testen tegen de gereedschappen die er al zijn.

**Signaal in je eigen werk:** als iemand voorstelt "we bouwen het bestaande koppelvlak na", is dat vaak een
goed idee. De vraag is niet of het mag, maar wat je erbij zet.

---

## Proef 2 · Waarom dit gevaarlijk is

**Wat je doet:** kijk nog eens naar het antwoord uit proef 1. Zoek naar het woord "proefopstelling",
"indicatief", "niet operationeel" of iets van die strekking.

**Wat je vindt:** niets. Het antwoord is technisch correct en zegt niets over zijn eigen status.

**Wat er onder de motorkap gebeurt.** Een koppelvlak is een afspraak over vorm, niet over betekenis. De
PI-standaard schrijft voor hoe een tijdreeks eruitziet, niet of hij ergens op slaat. Twee systemen kunnen
perfect met elkaar praten en het volstrekt oneens zijn over wat ze uitwisselen.

Zodra dit adres in een configuratiebestand terechtkomt — en configuratiebestanden overleven de mensen die
ze schreven — is er niets meer dat vertelt waar deze cijfers vandaan komen.

**Signaal in je eigen werk:** je krijgt een koppeling aangeboden die "gewoon werkt met jullie bestaande
systeem". Vraag dan niet of het werkt maar wat er achter zit, en wie er belt als het stilvalt.

**Wat je checkt:** staat er in de data zelf, of in de metadata, wat de status is van deze bron? Niet in de
documentatie — in het antwoord.

---

## Proef 3 · De vraag die je leert stellen

Voor functioneel beheerders is dit de meest bruikbare module van de hele route, want dit is precies de
situatie waarin je straks moet uitleggen waarom iets eruitziet als de echte dienst en het niet is.

Drie vragen die je dan stelt:

| vraag | waarom |
|---|---|
| Wie is de bronhouder, en staat dat in het antwoord? | een adres zegt niets over herkomst |
| Wat is de status: operationeel, pilot, of proefopstelling? | en staat die status ergens machineleesbaar? |
| Wat gebeurt er als dit adres wegvalt of iets anders gaat leveren? | een koppeling die stil verandert, is erger dan een die stopt |

**Wat je checkt:** noem één koppeling in jouw organisatie waarvan je niet weet wie hem beheert. Die is er
bijna altijd, en dat is de koppeling waar dit over gaat.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De waarschuwing stond eerst in een voetnoot.** Bij het opzetten van dit atelier is expliciet besloten
  hem in de module zelf te zetten en niet eronder. De redenering staat in het plan: een emulatie die
  overtuigend genoeg is om nuttig te zijn, is overtuigend genoeg om verkeerd begrepen te worden.
- **De emulatie draagt zijn status niet in de data.** Alle waarschuwingen staan in de module en op de
  pagina — geen enkele in het JSON-antwoord zelf. Wie het endpoint rechtstreeks aanroept, ziet niets. Dat
  is een open punt, niet iets wat opgelost is.
- **De emulatie is bereikbaar zonder dat je deze module gelezen hebt.** Het pad staat in de
  API-beschrijving van het Waterlab en is voor iedereen op de machine te vinden.

---

## Wat je hiervan meeneemt

Voor je beheerkaart, bij de vraag over escalatie:

| vraag | jouw antwoord |
|---|---|
| Welke koppelingen leveren data waarvan de status niet in de data staat? | |
| Wie zou het merken als er iets anders uit kwam dan verwacht? | |
| Staat er ergens machineleesbaar of een bron operationeel is? | |

**Volgende:** module W2, over wat er misging toen dit model met echte gegevens gevoed werd.
