---
id: k07-de-sleutelbos
titel: "De sleutelbos — twaalf proefopstellingen beheersbaar maken"
spoor: basis
volgorde: 70
competenties: [B4, B5]
duur_min: 25
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "voor je eigen toepassing benoemd wat je kwijt bent als de beheerlaag verdwijnt"
poc: labs-mcp
routes: []
---

# De sleutelbos

De vorige module ging over één toepassing draaiend houden. Deze gaat over wat er gebeurt als het er
dertien worden.

Op deze machine staan inmiddels dertien projecten. Twaalf ervan hebben sleutels nodig: een
API-token, een wachtwoord, een sleutel voor een externe dienst. Die stonden alle twaalf ergens anders —
in een `.env`-bestand hier, in een systemd-instelling daar, en soms alleen in het hoofd van degene die
het had gebouwd.

Dat is geen luxeprobleem. Het is de meest voorspelbare manier waarop een proefopstelling stukloopt:
niet omdat het model iets verzint, maar omdat een sleutel is verlopen en niemand meer weet waar hij
stond.

Deze module kost **geen modelbeurten**.

---

## Wat hier gebouwd is

Eén versleutelde kluis, en een programma dat de sleutels daaruit naar de juiste plek schrijft.

| onderdeel | wat het is | omvang |
|---|---|---|
| `labsctl` | de kern: kluis, uitrollen, controleren — een gewoon opdrachtregelprogramma | 284 regels |
| `mcp_server.py` | een dun laagje eromheen waardoor een AI-assistent dezelfde vijf handelingen kan doen | 71 regels |

De kluis zelf is één versleuteld bestand plus een sleutelbestand, buiten elke git-map, alleen leesbaar
voor de eigenaar. De vijf handelingen zijn: opsommen, ophalen, wegschrijven, uitrollen naar een
toepassing, en controleren of er iets verlopen of gelekt is.

### Wat een MCP-server is, zonder mystiek

MCP staat voor *Model Context Protocol*. Het is een afspraak over hoe een AI-assistent gereedschap mag
aanroepen dat op jouw machine staat. Meer is het niet: een lijst met handelingen, wat elk verwacht, en
wat het teruggeeft.

Het aardige eraan is wat er **niet** in zit. De assistent krijgt geen toegang tot de kluis. Hij krijgt
toegang tot vijf handelingen, en die handelingen bepalen zelf wat ze wel en niet teruggeven. `secret_list`
geeft namen en of iets binnenkort verloopt — nooit een waarde. Uitrollen herstart pas een dienst nadat een
mens dat heeft bevestigd.

Dat is de vorm waarin dit soort gereedschap veilig is: **niet de sleutelkast opengooien, maar een luikje
maken waar precies één ding doorheen past.**

---

## De eerste stap, en wat er nog ligt

Van die twaalf zijn er **twee** aangesloten:

| profiel | schrijft naar | herstart |
|---|---|---|
| `derwisch-ritueel` | `/etc/derwisch/ritueel.env` | `derwisch_local-ritueel.service` |
| `sysmonitor` | `/home/bob/sysmonitor/.auth` | `sysmonitor-web.service` |

Twee van de twaalf. Dat is met opzet het eerlijke getal in deze module: het is een eerste stap, geen
opgeloste situatie. De andere tien hebben hun sleutels nog op de oude plek staan, en bij minstens één
project staan er vier levende sleutels in een `.env`-bestand dat lang niet in `.gitignore` stond.

**De latere fase** is de rest aansluiten, zodat er één plek is waar je kunt zien welke sleutel waar wordt
gebruikt en wanneer hij verloopt. Dat is de opbrengst waar het om gaat — niet de versleuteling, maar het
**overzicht**. De vraag "welke van mijn twaalf toepassingen valt volgende maand om?" moet met één
opdracht te beantwoorden zijn.

Merk op wat dat over beheerlast zegt. Het bouwen van een proefopstelling is een middag werk. Het
beheersbaar houden van twaalf ervan is een apart project, en dat project was hier nodig na ongeveer vijf
maanden.

---

## Het dilemma: hoe open is open?

Hier zit een keuze die je in je eigen organisatie ook zult tegenkomen, en die minder eenvoudig is dan
"open source is goed".

**Wat er voor pleit.** MCP is een open afspraak. De specificatie is gepubliceerd, de bibliotheken staan
onder een vrije licentie, iedereen mag er een eigen implementatie van maken. Er zit geen factuur aan
vast en geen contract. Het alternatief — een commerciële sleutelkluis van een leverancier — is een veel
zwaardere afhankelijkheid: die kost geld, staat vaak in een cloud, en verhuizen is een project op zich.

**Wat er tegen pleit.** Open is niet hetzelfde als onafhankelijk. Dit protocol is bedacht door één
leverancier, het is jong, en de programma's die het vandaag spreken komen grotendeels van diezelfde
leverancier. Als je je *beheer* van twaalf systemen erop bouwt, hangt niet alleen je modelkeuze maar je
hele bedrijfsvoering aan een afspraak waarvan je de koers niet bepaalt. Een licentie beschermt je tegen
een factuur. Ze beschermt je niet tegen een leverancier die volgend jaar iets anders wil.

Datzelfde geldt een laag dieper. De versleuteling hier gebruikt `age`: klein, leesbaar, goed te
controleren. Maar het is ook een klein project met een kleine gemeenschap. Als het wordt verlaten, moet
alles opnieuw versleuteld worden.

**Hoe het hier is opgelost.** Door de afhankelijkheid zo dun mogelijk te maken. De kern is een gewoon
opdrachtregelprogramma dat alleen de standaardbibliotheek gebruikt; de MCP-server is een schil van 71
regels eroverheen. Valt MCP weg, dan verlies je het gemak dat een assistent dit voor je doet — niet je
sleutelbeheer. En elk aangesloten project houdt een meegeleverd voorbeeldbestand, zodat het na
binnenhalen van de broncode gewoon draait, **zonder kluis en zonder MCP**.

> De kluis is beheer-gemak, geen draaivereiste.

Dat is de vraag die je zelf moet stellen, en het is een andere vraag dan die meestal wordt gesteld. Niet
"is het open source?" maar:

**Wat ben ik kwijt op de dag dat dit verdwijnt?**

Als het antwoord "een gemak" is, is de afhankelijkheid goed gelegd. Als het antwoord "mijn productie" is,
maakt de licentie het niet minder erg.

---

## Wat hier misging

Twee dingen, en het tweede is het leerzaamste.

**Het gereedschap dat lekken moest opsporen, lekte zelf.** Bij het bouwen van deze kluis is er een
ontwerpdocument geschreven en een test. In allebei stonden **echte wachtwoorden** als voorbeeld — precies
de waarden die de kluis moest gaan beschermen. Ze zijn er later uit gehaald, maar ze hadden er nooit in
mogen staan, en in de geschiedenis van de broncode zijn ze niet vanzelf weg.

Dit is de meest voorkomende manier waarop sleutels weglekken: niet via een inbraak, maar via een
voorbeeld, een schermafdruk, een testbestand of een gesprek. De reflex "ik zet even de echte waarde
erin, dan werkt het" is de bron. In dit atelier is dezelfde fout tijdens het bouwen nog een keer gemaakt:
een sleutel voor de tunneldienst is in een gesprek geplakt en moet daarom worden vervangen.

**De lekcontrole gaf eerst onzin.** De controle die kijkt of een sleutel ergens publiek te vinden is,
haalde de publieke pagina op zonder zich als browser voor te doen. De beveiliging ervoor gaf een
weigering terug, de controle zag geen lek, en meldde dus "in orde". Een controle die bij twijfel
"in orde" zegt is gevaarlijker dan geen controle, want je gaat erop vertrouwen. Daarna zocht dezelfde
controle op korte, veelvoorkomende waarden zoals gebruikersnamen, en meldde overal een lek.

Beide fouten zijn dezelfde fout uit **K4**, alleen zonder taalmodel: een systeem dat een stellig antwoord
geeft over iets wat het niet werkelijk heeft gecontroleerd.

---

## Opdracht

Beantwoord voor je eigen toepassing:

1. Waar staan de sleutels van je toepassing nu, en wie weet dat?
2. Welke ervan verloopt, en wat merk je op de dag dat dat gebeurt?
3. Als je een beheerlaag zou invoeren: wat ben je kwijt op de dag dat die laag wegvalt? Is dat een
   gemak, of je productie?

Vraag drie hoort op je beheerkaart. De volgende module is die kaart.
