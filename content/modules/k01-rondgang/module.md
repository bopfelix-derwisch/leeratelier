---
id: k01-rondgang
titel: "Rondgang — dertien dingen op één machine"
spoor: basis
volgorde: 10
competenties: [B1]
duur_min: 20
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "invulschema van één POC: welke onderdelen zitten erin"
poc: alle
routes: []
---

# Rondgang

Je staat in een serverkast ter grootte van een schoenendoos. Daarin draaien dertien projecten, zeventien
diensten en drie taalmodellen, en het geheel trekt minder stroom dan een waterkoker.

Deze module kost **geen modelbeurten**. Je kijkt alleen.

**Wat je nodig hebt:** je browser.

---

## Wat je gaat zien

| | |
|---|---|
| Eén machine | NVIDIA Jetson AGX Orin, 61 GB geheugen dat processor en GPU **delen** |
| Zeventien diensten | van een chatbot tot een knop die een ritueel start |
| Drie taalmodellen | tegelijk in het geheugen, samen ongeveer 25 GB |
| Dertien projecten | waarvan er zes publiek bereikbaar zijn |

De les van deze module is niet dat het veel is. De les is dat je van elk onderdeel kunt zeggen **waar het
zit, wat het kost en wat er stukgaat als het wegvalt** — en dat dat bij de meeste AI-toepassingen die je
in je werk tegenkomt niet lukt.

---

## Eerst: waarom dit er staat

Voordat je onder de motorkap kijkt, de vraag die daaraan voorafgaat. Waarom zou je dit willen?

Dit zijn dertien werkende toepassingen, gebouwd in zeven maanden door één persoon naast ander werk.
Een hydrologische verwachting voor de IJssel. Een vergunningenchatbot op echte wetteksten. Geluid, lucht
en externe veiligheid als deelbaar informatieproduct. Een reflectie-instrument voor beroepsethiek. Een
bewakingsdienst die zichzelf en de rest in de gaten houdt.

Dat is de eerste helft van het verhaal, en het is de helft die verkoopt: **de kosten van uitproberen
zijn ingestort.** Een idee dat vijf jaar geleden een project van maanden was met een offerte eraan vast,
is nu een middag. Wie een vraag heeft, kan er nu een werkend antwoord naast leggen in plaats van een
business case.

Er hoort bij hoe dit gebouwd is: niet door een ontwikkelteam, maar door één persoon die geen
programmeur van beroep is, in gesprek met een AI-assistent. Dat heet **vibe coding**, en het verklaart
het tempo. Het verklaart ook de keerzijde die je in elke foutensectie van deze route terugziet: je hebt
sneller iets dat werkt dan iets dat je over een jaar nog kunt uitleggen.

De tweede helft is waar het in organisaties werkelijk vastloopt, en zeker bij de overheid: **opschalen.**
Dertien proefopstellingen op één machine is iets heel anders dan drie toepassingen in productie met
duizend gebruikers, een beheerorganisatie, een aanbesteding en een functionaris gegevensbescherming.
De eerste is een middag. De tweede is een programma.

Wat er tussen die twee in zit, is precies wat je hieronder gaat bekijken. **De drie proeven zijn geen
technische rondleiding maar drie opschaalvragen:**

| proef | de vraag hier | dezelfde vraag bij opschalen |
|---|---|---|
| **1. Wat draait er?** | wat staat er, wat valt om | wie beheert er vijftig, met welke eigenarenlijst? |
| **2. Wat kost het?** | tijd en geheugen per antwoord | wat bij honderd gebruikers, wie betaalt dat? |
| **3. Waar zit de kennis?** | welke bron, hoe oud | wie houdt vijftig indexen actueel? |

De linkerkolom kun je vanmiddag beantwoorden. De rechterkolom is waarom een geslaagde proef nog geen
geslaagde invoering is — en waarom de vraag "kan het?" allang niet meer de interessante vraag is. Die is
"kunnen wij het dragen?", en dat is een beheervraag, geen technische.

Houd die rechterkolom erbij terwijl je de drie proeven doet. Aan het eind van de module kom je erop terug.

---

## Proef 1 · Wat draait er eigenlijk?

Open **[de statuspagina van deze machine](https://status.felixisfelix.com/)**. Je ziet de bewaakte systemd-diensten, elk met een
status, en bovenaan een blok "handelingsperspectief": per waarschuwing een concreet commando.

**Wat je doet:** zoek er drie uit en probeer per dienst te benoemen wat er gebeurt als hij wegvalt.

**Wat er onder de motorkap gebeurt.** Elke dienst is een `systemd`-unit: een tekstbestandje dat zegt welk
commando gestart moet worden, als welke gebruiker, en wat er moet gebeuren als het proces stopt. Meer is
het niet. De diensten van dit atelier staan op `Restart=always`, want het atelier draait onbewaakt.

**Het signaal in je eigen werk:** vraag bij elke AI-toepassing welke processen er draaien en wie ze
herstart als ze omvallen. Als het antwoord "dat regelt de leverancier" is, vraag dan door: hoe merkt die
het, en hoe snel?

**Wat je checkt:** bestaat er een lijst van draaiende onderdelen met per onderdeel een eigenaar? Dat is
één tabel, en het ontbreken ervan zegt meer dan de inhoud.

---

## Proef 2 · Wat kost het?

| | |
|---|---:|
| Geheugen in gebruik | ongeveer 38 van 61 GB |
| Modellen op schijf | 77 GB |
| Schijf `/` | 82 procent vol |
| Schijf `/mnt/nvme` | 85 procent vol |

**Wat er onder de motorkap gebeurt.** Het geheugen is *unified*: processor en GPU delen dezelfde 61 GB.
Een taalmodel dat 19 GB groot is, neemt die 19 GB dus af van alles wat er verder draait. Dat is de reden
dat op deze machine geen twee grote modellen naast elkaar passen — bij een poging daartoe bleef er 0,5 GB
over, en dan faalt de eerstvolgende toewijzing van wat dan ook.

**Het signaal in je eigen werk:** "de AI-toepassing draait in de cloud" betekent niet dat deze kosten
verdwijnen. Ze staan alleen op een andere factuur, en die is meestal per verwerkte vraag.

**Wat je checkt:** wat kost één antwoord? Niet in euro's, maar in tijd en geheugen. Als niemand dat weet,
weet ook niemand wat er gebeurt bij tien keer zoveel gebruikers.

---

## Proef 3 · Waar zit de kennis?

Neem één POC — de vergunningen-chatbot is de duidelijkste — en probeer de onderdelen te benoemen.

| onderdeel | wat het is | waar het zit |
|---|---|---|
| bron | IPLO-webpagina's over de Omgevingswet | op internet, van iemand anders |
| bewerking | HTML strippen, in stukken van 1200 tekens knippen | een script van twintig regels |
| embeddings | elk stuk omgezet in 1024 getallen | een model van 1,1 GB op poort 8082 |
| index | die getallen in één bestand | 3,8 MB op schijf |
| model | schrijft het antwoord | 5 GB op poort 8081 |
| weergave | de chatpagina | een webpagina |

**Wat er onder de motorkap gebeurt.** Bij een vraag worden de best passende stukken uit de index gehaald
en aan het model meegegeven. Het model schrijft daar een antwoord bij. Dat is de hele truc.

**Het signaal in je eigen werk:** als een leverancier "AI" zegt, vraag welke van deze zes onderdelen ze
zelf beheren en welke ze inkopen. Meestal is dat drie en drie, en de scheidslijn bepaalt wie je belt.

**Wat je checkt:** kun je van elk onderdeel zeggen wie het bijwerkt en hoe vaak? Dit invulschema is het
bewijsstuk van deze module.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

Het opzetten van dit atelier begon met een inventarisatie van de projecten. Dat leverde meer op
over het beheer dan over de techniek.

- **Geen van de tien repositories had een licentie.** Niet negen van de tien — geen enkele. Zonder
  licentiebestand is code juridisch "alle rechten voorbehouden", ook code die je zelf publiek zet. Dat is
  op 3 september 2026 rechtgezet met Apache-2.0.
- **Drie projecten stonden helemaal niet onder versiebeheer.** Waaronder de monitoringdienst die de
  storingen van alle andere moet melden. Geen geschiedenis, geen weg terug.
- **Er stonden vier echte sleutels in een bestand dat niet genegeerd werd.** Een projectmap had geen
  `.gitignore` en bevatte een `.env` met tokens voor OpenAI, GitHub, Cloudflare en Vercel. Het bestand was
  nog niet meegecommit, maar één achteloos commando had ze publiek gemaakt. Dit is de reden dat een
  geheimencheck vóór de eerste commit gaat en niet erna.
- **Een wachtwoord staat nog in de geschiedenis.** In een ander project staat een PIN als vaste waarde in
  de broncode én in een overdrachtsdocument, verspreid over twee commits. Daar helpt een `.gitignore` niet
  meer tegen: wat eenmaal in de geschiedenis zit, krijg je er alleen uit door die geschiedenis te
  herschrijven. Het staat nog open.
- **De naam van een project klopte niet meer met zijn eigen API.** Een POC heette ooit "Geluidsmeter" en
  is hernoemd toen geluid één van meerdere onderwerpen werd. In de technische beschrijving stond de oude
  naam er nog maanden later in — zichtbaar voor iedereen die het bestand opende.

Wat deze vijf gemeen hebben: het zijn allemaal dingen die je pas ziet als je gaat kijken, en die
ondertussen niets kapotmaken. Precies daarom blijven ze staan.

---

## Wat je hiervan meeneemt

Voor de beheerkaart:

| Vraag | Waarom hij ertoe doet |
|---|---|
| Welke onderdelen zitten er in deze toepassing? | zonder die zes vakjes weet je niet wie je belt |
| Wat kost één antwoord aan tijd en geheugen? | dat bepaalt wat er gebeurt bij groei |
| Wie werkt elk onderdeel bij, en hoe vaak? | het antwoord "niemand" komt vaker voor dan je denkt |
| Wat gaat er stuk als dit onderdeel wegvalt? | per onderdeel, niet voor het geheel |

**En de rechterkolom van hierboven.** Je hebt nu drie keer de kleine versie van een opschaalvraag
beantwoord. Neem ze mee in de grote vorm, want dit is waar een geslaagde proef alsnog strandt:

- Bij vijftig toepassingen is de vraag niet of ze werken, maar of er een lijst bestaat met per
  onderdeel een eigenaar. Die lijst is er hier ook pas sinds kort.
- Bij honderd gelijktijdige gebruikers is de vraag niet of het model goed genoeg is, maar of er
  hardware en budget zijn, en of iemand weet wat één antwoord kost.
- Bij vijftig bronnen is de vraag niet of de zoekindex klopt, maar wie merkt dat hij dat niet meer doet.

Als je in je eigen organisatie één ding uit deze module meeneemt: **de proef bewijst dat het kan, niet
dat je het kunt dragen.** Dat zijn twee besluiten, en ze worden vaak als één behandeld.

**Volgende:** module K4 laat zien hoe een antwoord uit deze keten fout kan gaan — op vijf verschillende
manieren.
