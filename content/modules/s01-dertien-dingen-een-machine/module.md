---
id: s01-dertien-dingen-een-machine
titel: "Dertien dingen op een machine — de rondgang"
spoor: sturing
volgorde: 10
competenties: [M1, M4]
duur_min: 20
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "van een eigen toepassing benoemd wat er zou gebeuren als de bouwer morgen weggaat"
poc: sysmonitor
routes: ["/"]
---

# Dertien dingen op een machine

Voor je staat een kastje ter grootte van een schoenendoos. Daarin draaien dertien projecten, zeventien
diensten en drie taalmodellen, en het geheel trekt minder stroom dan een waterkoker.

Deze module kost **geen modelbeurten**.

**Wat je nodig hebt:** je browser.

---

## Wat hier in zeven maanden is gebouwd

Dertien werkende toepassingen, door één persoon naast ander werk. Een hydrologische verwachting voor
de IJssel. Een vergunningenchatbot op echte wetteksten. Geluid, lucht en externe veiligheid als
deelbaar informatieproduct. Een reflectie-instrument voor beroepsethiek. Een bewakingsdienst die de
rest in de gaten houdt.

Dat is het cijfer dat je moet onthouden, en niet omdat het indrukwekkend is. **De kosten van
uitproberen zijn ingestort.** Een idee dat vijf jaar geleden een project van maanden was met een
offerte eraan vast, is nu een middag werk. Dat verandert wat een verkenning waard is: je kunt naast
een vraag een werkend antwoord leggen in plaats van een business case.

En daar zit meteen de valkuil van deze fase. Dertien geslaagde proeven zeggen iets over de
haalbaarheid van het idee, en vrijwel niets over de haalbaarheid van de **invoering**. Dat is de
scheidslijn waar het in organisaties werkelijk misgaat, en zeker bij de overheid:

| | een proef | in productie |
|---|---|---|
| **Beheer** | de bouwer weet het | een organisatie moet het weten |
| **Beschikbaarheid** | het draait als je kijkt | het draait ook 's nachts, en iemand wordt gebeld |
| **Inkoop** | niets | aanbesteding, contract, exit-afspraken |
| **Gegevens** | een map met testdata | verwerkersovereenkomst, bewaartermijn, FG |
| **Kosten** | een apparaat | hardware, licenties, en uren die niemand had begroot |

Geen van deze vijf is een technisch probleem, en geen van vijf wordt opgelost door een betere proef.
Ze zijn ook niet de reden om niet te beginnen -- ze zijn de reden om **vooraf te weten waarvoor je
tekent**, en dat is precies wat deze route je wil geven.

Houd die rechterkolom erbij bij alles wat hierna komt.

---

## De schaal is het probleem niet

| | |
|---|---|
| Eén machine | NVIDIA Jetson AGX Orin, 61 GB geheugen dat processor en grafische kaart **delen** |
| Zeventien diensten | van een chatbot tot een knop die een dagelijks ritueel start |
| Drie taalmodellen | tegelijk in het geheugen, samen ongeveer 25 GB |
| Dertien projecten | waarvan er zes publiek bereikbaar zijn |

Die twee getallen staan los van elkaar, en dat is geen slordigheid. **Eén project kan meerdere diensten
hebben:** Derwisch heeft er vier, het Leeratelier drie, Morele Helper en LeefomgevingLab elk twee. En
twee diensten horen bij geen enkel project — die regelen de netwerktoegang voor alle andere.

Dat onderscheid is meteen de eerste beheervraag van deze route. Een project is wat je bespreekt in een
overleg; een dienst is wat 's nachts omvalt. De tweede lijst is bijna altijd langer dan de eerste, en
bijna nooit degene die iemand kan opnoemen.

Kijk zelf op **[de statuspagina](https://status.felixisfelix.com)**. Die is openbaar en toont wat er
draait, hoe vol de schijf zit en wat er misgaat.

Het punt van deze module is niet dat het veel is. Het punt is dat je van elk onderdeel kunt zeggen
**waar het staat, wat het kost en wat er stukgaat als het wegvalt** — en dat dat bij de meeste
AI-toepassingen die je in je werk tegenkomt niet lukt.

Probeer het eens voor een toepassing in je eigen organisatie. Waar draait die? Welk model gebruikt hij,
en van wie is dat? Waar komen de gegevens vandaan waarop hij antwoordt? Wie merkt het als die
gegevens verouderen? In de meeste gevallen kom je bij de derde vraag al niet verder zonder te bellen.

---

## Wat schaars is, is niet wat je denkt

Deze modellen draaien lokaal. Er is geen abonnement en geen prijs per vraag. Toch zit er een budget op:
driehonderd vragen per dag.

De reden is capaciteit, niet geld. Uit de meting op deze machine:

> De grafische kaart staat op 93 tot 96 procent **bij één enkele gebruiker**. Gelijktijdigheid koopt
> doorzet met wachttijd, niet met extra werk.

Er is één zo'n kaart, en alle dertien projecten delen hem. Een drukke ochtend in dit atelier maakt de
andere toepassingen op dezelfde machine trager. Dat is de vorm die schaarste hier aanneemt: niet een
rekening aan het eind van de maand, maar een collega die klaagt dat het traag is.

Onthoud die verschuiving. Bij lokale AI verhuist de kostenvraag van de begroting naar de capaciteits-
en beheerkant, en die staat zelden in een offerte.

---

## Wat hier misging

Het opzetten van dit atelier begon met een inventarisatie van alle projecten op deze machine. Dat
leverde meer op over het beheer dan over de techniek.

- **Geen van de tien repositories had een licentie.** Niet negen van de tien — geen enkele. Zonder
  licentiebestand is code juridisch "alle rechten voorbehouden", ook code die je zelf publiek zet.
  Dat is op 3 september 2026 rechtgezet.
- **Drie projecten stonden helemaal niet onder versiebeheer.** Waaronder de monitoringdienst die de
  storingen van alle andere moet melden. Geen geschiedenis, geen weg terug, en van alle diensten juist
  degene die je zou moeten vertrouwen.
- **Er stonden vier levende sleutels in een bestand dat niet werd genegeerd.** Eén verkeerde publicatie
  en ze stonden op internet.

Dit is de kern van deze module. Er was hier geen enkel technisch probleem — alles deed het. Wat ontbrak
was het saaie werk eromheen: licentie, versiebeheer, sleutelbeheer, en iemand die het overziet. Precies
de dingen waar niemand om vraagt in een demo, en precies de dingen waar je als opdrachtgever wél voor
tekent.

Bij een proefopstelling van een enthousiasteling is dat te overzien. Bij een toepassing die je
organisatie in productie neemt, is het een openstaande rekening.

---

## Opdracht

Neem één AI-toepassing in je organisatie, of één die je overweegt, en beantwoord:

1. Staat de code onder versiebeheer, en wie kan dat aantonen?
2. Onder welke licentie mag je hem gebruiken, aanpassen en meenemen naar een andere leverancier?
3. Wat gebeurt er als de bouwer morgen vertrekt? Noem de naam van degene die het dan overneemt.

Vraag 3 is de belangrijkste, en het antwoord "dat regelen we dan" is geen antwoord. Het komt terug op
je besluitkaart.
