---
id: s02-wat-je-koopt
titel: "Wat je koopt als je AI koopt"
spoor: sturing
volgorde: 20
competenties: [S1, S3]
duur_min: 25
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de zes onderdelen ingevuld voor een eigen toepassing, met per onderdeel een eigenaar"
poc: leefomgevinglab
routes: ["/kwaliteit"]
---

# Wat je koopt als je AI koopt

Wie een AI-toepassing aanschaft, denkt een model te kopen. Dat is het goedkoopste en meestal het minst
belangrijke onderdeel.

Deze module kost **geen modelbeurten**.

---

## Zes onderdelen, zes eigenaren

Een toepassing als de vergunningen-chatbot op deze machine bestaat uit zes dingen. Ze staan hier met de
enige vraag die er voor jou toe doet: **wie is hiervan de eigenaar, en wat gebeurt er als het veroudert?**

| onderdeel | wat het is | de vraag die je stelt |
|---|---|---|
| **Het model** | het taalmodel dat de zinnen maakt | Van wie is het? Wat als de voorwaarden veranderen? |
| **De bron** | de documenten waarop het antwoordt | Wie beheert die, en hoe vaak verandert hij? |
| **De index** | de doorzoekbare vorm van die bron | Wanneer is die voor het laatst ververst, en wie merkt het als dat niet gebeurt? |
| **De ophaalstap** | het zoeken naar passende stukken bron | Hoeveel stukken, en wat als het antwoord er niet in staat? |
| **De instructie** | de vaste tekst die het model meekrijgt | Wie mag die wijzigen, en wordt dat vastgelegd? |
| **Het contract** | de regels over wat het systeem mag beweren | Wat doet het als het iets niet weet? |

Van deze zes wordt er in een verkoopgesprek meestal één besproken: het model. Dat is ook het onderdeel
dat je het makkelijkst kunt vervangen. De andere vijf zijn waar het werk zit, en waar het misgaat.

**De index is het onderdeel dat je moet onthouden.** Een chatbot die "op je eigen documenten" antwoordt,
antwoordt in werkelijkheid op een kopie daarvan, gemaakt op een moment in het verleden. Hoe oud die kopie
is, zie je aan het antwoord niet. Vraag ernaar. Vraag ook wie merkt dat hij oud wordt.

---

## Kijk hoe anderen dit opschrijven

Het LeefomgevingLab op deze machine houdt per gegevensbron bij wat er niet aan klopt. Dat staat
openbaar op **[de kwaliteitspagina](https://leefomgevinglab.felixisfelix.com/kwaliteit)**.

Neem even de tijd voor die pagina. Ze is opgeschreven door de mensen die het hebben meegemaakt, niet
door iemand die het achteraf mooi moest maken, en dat verschil zie je meteen. Onderaan staat een blokje
"wat steeds terugkomt". Dat blokje is de opbrengst van maanden werk.

**Dit is wat je zou moeten vragen van een leverancier.** Niet een verkooppraatje over betrouwbaarheid,
maar een pagina waarop staat wat er níét goed gaat. Wie dat niet kan leveren, heeft het niet
bijgehouden.

---

## Wat hier misging

De zoekindex van de vergunningen-chatbot van dit lab was **33 kilobyte**. Bij de gebruikte techniek komt
dat neer op ongeveer acht stukjes tekst.

Acht. Er stond een werkende chatbot, met een net antwoordvenster en bronvermelding eronder, die
inhoudelijk vrijwel niets tot zijn beschikking had. Hij gaf antwoord, want dat doet een taalmodel altijd.
Alleen kwam dat antwoord niet uit de bron waarnaar de opzet verwees.

Aan de buitenkant was daar niets van te zien. Geen foutmelding, geen lege pagina, geen waarschuwing.
Het is pas gevonden doordat iemand de bestandsgrootte opzocht — een handeling van vijf seconden die in
maanden niemand had verricht. De index is daarna herbouwd naar 924 stukjes.

De les voor jou: **"hij draait" en "hij werkt" zijn twee verschillende beweringen**, en de eerste zegt
niets over de tweede. Bij klassieke software vallen ze meestal samen. Hier niet.

---

## Opdracht

Vul de tabel hierboven in voor één toepassing uit je eigen organisatie. Zes rijen, en per rij een naam
of een rol als eigenaar.

Bij hoeveel rijen kom je eruit zonder te bellen? Dat aantal is een eerlijker maat voor je grip op die
toepassing dan welk voortgangsrapport ook.
