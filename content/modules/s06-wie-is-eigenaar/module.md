---
id: s06-wie-is-eigenaar
titel: "Wie is eigenaar als het misgaat"
spoor: sturing
volgorde: 60
competenties: [M5, M6]
duur_min: 20
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "voor een eigen toepassing een naam ingevuld bij eigenaarschap, exit en sleutelbeheer"
poc: null
routes: []
---

# Wie is eigenaar als het misgaat

De vorige module ging over wat het kost. Deze gaat over wie de rekening krijgt, en wie er staat als het
werkelijk fout loopt.

Deze module kost **geen modelbeurten**.

---

## Vier vragen die pas achteraf urgent worden

**1. Van wie is de code, en mag je ermee weg?**
Zonder licentiebestand is code juridisch "alle rechten voorbehouden" — ook code die je zelf publiek zet,
en ook code waar je voor betaald hebt. Vraag bij oplevering niet of de code "van jou" is, maar onder welke
licentie, en laat het bestand zien.

**2. Waar staan de sleutels?**
Elke toepassing heeft toegangssleutels: een token, een wachtwoord, een sleutel voor een externe dienst.
De vraag is niet of ze veilig zijn opgeborgen. De vraag is of **iemand kan opnoemen waar ze staan en
wanneer ze verlopen**. Kan niemand dat, dan is de eerstvolgende storing er een waarbij niemand weet
waarom.

**3. Wat wordt er gelogd, en wat zeg je daarover tegen je mensen?**
Dit atelier legt vragen vast, negentig dagen lang, en zegt dat op de inlogpagina. Dat is geen
formaliteit: wie zelf gelogd wordt, snapt beter waarom logging nodig is. Bij je eigen toepassing is de
vraag wie de vragen van medewerkers kan teruglezen, en of die medewerkers dat weten.

**4. Hoeveel mensen kunnen dit overnemen?**
Als het antwoord één is, heb je geen toepassing maar een persoonsafhankelijkheid met een
gebruikersinterface.

---

## De ruil die je aangaat

Bij een leverancier is de continuïteit contractueel geregeld en betaal je ervoor. Bij eigen beheer is ze
niet geregeld en betaal je er ook voor, alleen zie je dat pas als er iets gebeurt.

Geen van beide is fout. Wat fout is, is de ruil niet expliciet maken. Op deze machine staat die keuze
zwart op wit in de openstaande vragen, en het antwoord is er nog niet:

> **Wie kan dit beheren behalve jij?** Bij permanent bedrijf is dit een groter risico dan bij
> dagvensters. Tweede persoon met toegang, óf de verwachting expliciet verlagen op de inlogpagina.

Merk op wat de tweede optie zegt: als je het risico niet kunt wegnemen, kun je het nog wel **eerlijk
opschrijven** waar gebruikers het zien. Dat is een legitieme keuze en vaak de enige haalbare.

---

## Wat hier misging

Drie keer hetzelfde, in oplopende gênantheid.

**In een projectmap stonden vier levende sleutels** in een bestand dat niet werd genegeerd door het
versiebeheer. Eén verkeerde publicatie en ze stonden op internet.

**Er is een kluis gebouwd om dat op te lossen** — één versleutelde plek voor alle sleutels. In het
ontwerpdocument van die kluis en in een testbestand stonden **echte wachtwoorden** als voorbeeld. Precies
de waarden die de kluis moest beschermen. Ze zijn eruit gehaald, maar in de geschiedenis van de code
staan ze nog.

**En tijdens het bouwen van dit atelier** is een toegangssleutel voor de tunneldienst in een gesprek
geplakt. Daarmee geldt hij als gelekt en moet hij worden vervangen.

Drie keer dezelfde oorzaak, en het is niet onkunde: het is de reflex *"ik zet even de echte waarde erin,
dan werkt het"*. Sleutels lekken zelden door een inbraak. Ze lekken via een voorbeeld, een
schermafdruk, een testbestand of een gesprek — allemaal momenten waarop iemand iets nuttigs aan het doen
was.

Wat je eruit meeneemt: vraag bij een oplevering niet of de beveiliging op orde is. Vraag **wie er zou
merken dat een sleutel gelekt is, en waaraan**. Bij de drie gevallen hierboven was dat antwoord twee keer
"niemand".

---

## Opdracht

Voor één toepassing in je organisatie, en het antwoord is telkens een naam of een rol:

1. Wie is eigenaar als het misgaat? Geen afdeling — een persoon.
2. Wie neemt het over als die persoon vertrekt, en weet die persoon dat?
3. Wie zou merken dat een sleutel gelekt is, en waaraan?

Kun je vraag 1 niet beantwoorden, dan is dat je belangrijkste bevinding van vandaag. Op de besluitkaart
is dit vraag 5.
