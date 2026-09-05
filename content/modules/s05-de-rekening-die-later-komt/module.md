---
id: s05-de-rekening-die-later-komt
titel: "De rekening die later komt"
spoor: sturing
volgorde: 50
competenties: [M4]
duur_min: 25
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de jaarlijkse beheerlast van een eigen toepassing geschat, in uren en in namen"
poc: sysmonitor
routes: ["/"]
---

# De rekening die later komt

Een proefopstelling bouw je in een middag. Er dertien beheersbaar houden is een apart project, en dat
was hier nodig na ongeveer vijf maanden.

Deze module kost **geen modelbeurten**.

---

## Waar de kosten werkelijk zitten

De aanschaf is het bedrag dat in je begroting staat. Deze vijf staan er meestal niet in.

**1. De index veroudert vanzelf.**
Iemand moet hem verversen, en iemand moet merken dat het niet is gebeurd. Op deze machine kost
herbouwen ongeveer drie minuten. Dat is niet het probleem. Het probleem is dat er drie maanden overheen
kunnen gaan voordat iemand het opmerkt, want een verouderde index geeft even vloeiende antwoorden als
een verse.

**2. De bron verandert zonder je te waarschuwen.**
Een veldnaam wijzigt, een adres verhuist, een coördinatenstelsel wordt anders genoteerd. Je leverancier
merkt dat niet; je gebruikers wel, maar die melden het als "hij doet raar".

**3. De onderliggende software gaat vooruit.**
Op deze machine geldt een harde regel: na elke opwaardering van de rekenlaag moet één specifieke
controle opnieuw worden gedraaid, omdat een bekende fout in de systeemsoftware een bepaald type model
laat vastlopen. Werkt vandaag, kan na een routineupdate stuk zijn. Zulke afhankelijkheden staan in geen
enkele offerte.

**4. Toezicht kost tijd, ook als er niets aan de hand is.**
Deze machine heeft een dagelijkse controle die zeventien diensten, vijf adressen, schijf, geheugen,
temperatuur en beveiliging nakijkt. Die is er niet voor de storing; die is er voor het vertrouwen dat er
geen storing is.

**5. Iemand moet het kunnen uitleggen, over een jaar.**
Dit is de duurste en de minst zichtbare. Zie de volgende module, over eigenaarschap.

---

## Lokaal draaien verschuift de rekening, het schrapt hem niet

Deze modellen draaien op eigen hardware. Geen abonnement, geen prijs per vraag, geen gegevens die de
deur uitgaan. Dat is een reële winst en het is de reden dat deze opstelling bestaat.

Maar de kosten zijn niet verdwenen, ze zijn van vorm veranderd:

| in de cloud | lokaal |
|---|---|
| een rekening per maand | een machine die je koopt, koelt en vervangt |
| capaciteit is elastisch | één grafische kaart, gedeeld door alles |
| de leverancier doet onderhoud | je doet onderhoud |
| leveranciersafhankelijkheid | kennisafhankelijkheid van één persoon |

De onderste regel is de belangrijkste. Je ruilt afhankelijkheid van een bedrijf in voor afhankelijkheid
van iemand die dit kan. Dat is soms een goede ruil, maar het is wel een ruil, en hij hoort in het besluit
te staan.

Kijk voor het capaciteitsverhaal ook naar **[de statuspagina](https://status.felixisfelix.com)**: daar
staat wat er nu draait en hoe zwaar het is belast.

---

## Wat hier misging

De bewaking van dit atelier gaf maandenlang een verkeerd advies, en het was stellig geformuleerd:

> Antwoorden duren 71,7 s — haal het showmodel uit de route, of verlaag `gelijktijdig.showmodel`.

Er klopte niets van. Die 71,7 seconden kwam van een heel ander onderdeel dan het genoemde model. Erger:
de berekening keek naar "de laatste vijftig antwoorden" zonder tijdvenster, dus één trage meting van
enkele dagen eerder zou de waarschuwing nog **maanden** hebben gevoed. En bij weinig metingen was de
uitkomst simpelweg het hoogste getal, zodat één losse testvraag als storing werd gepresenteerd.

Het is niet gevonden door de bewaking. Het is gevonden doordat iemand vroeg: *klopt dit eigenlijk wel?*

Dit is de reden dat toezicht in je begroting hoort en niet in de kleine lettertjes. **Een controle die
bij twijfel "in orde" of "er is een storing" zegt zonder werkelijk te kijken, is gevaarlijker dan geen
controle** — want je gaat erop vertrouwen, en je gaat ernaar handelen. In dit geval zou het advies je een
model hebben laten uitzetten dat niets met het probleem te maken had.

---

## Opdracht

Schat voor één toepassing in je organisatie:

1. Hoeveel uur per maand kost het bijhouden van de bron en de index, en van wie zijn die uren?
2. Wie kijkt of het nog klopt, en hoe zou die persoon het merken als het niet meer klopt?
3. Wat gebeurt er in het jaar dat er niets aan gebeurt?

Vraag 3 is geen strikvraag. Bij klassieke software is het antwoord vaak "niets, hij draait door". Hier
is het antwoord "hij wordt stilletjes minder juist", en dat verschil is de kern van deze module.
