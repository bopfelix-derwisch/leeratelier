---
id: l01-kwaliteit-per-poc
titel: "Kwaliteit per POC — wat steeds terugkomt"
spoor: leefomgeving
volgorde: 10
competenties: [B3]
duur_min: 25
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de terugkerende patronen herkend in je eigen bronnen"
poc: leefomgevinglab
routes: ["/kwaliteit", "/wfs-kwaliteit"]
---

# Kwaliteit per POC

LeefomgevingLab bestaat uit een handvol proefopstellingen die elk op echte open data of een
overheids-API draaien. Bij het bouwen liep het team steeds tegen dezelfde soort dingen aan, en die zijn
opgeschreven op een pagina die `/kwaliteit` heet.

Die pagina is het interessantste document van de hele machine, want het is geschreven door de mensen die
het hebben meegemaakt en niet door iemand die het achteraf mooi moest maken.

Deze module kost **geen modelbeurten**.

---

## Wat je gaat zien

De kwaliteitsaspecten worden per POC in zes categorieën beschreven:

| categorie | waar het over gaat |
|---|---|
| **Databron** | wat de bron is, hoe volledig, hoe actueel |
| **Geo/CRS** | coördinatenstelsels, asvolgorde, notatie |
| **API-contract** | paden, headers, veldnamen, foutcodes |
| **Performance** | hoe lang een aanroep duurt en waarom |
| **Antwoordkwaliteit & veiligheid** | wat het systeem beweert en wat het achterhoudt |
| **Onderhoudbaarheid** | wie dit over een jaar nog kan uitleggen |

Zes categorieën, en aan het eind van de pagina staat een blokje **"wat steeds terugkomt"**. Dat blokje is
de eigenlijke opbrengst van maanden werk.

---

## Proef 1 · Lees "wat steeds terugkomt"

Open `/kwaliteit` en scroll naar het eind.

De twee patronen die er als terugkerend staan genoteerd:

> **Geo/CRS** — *"Coördinaatstelsel is keer op keer de valkuil: RD vs WGS84, asvolgorde, en de
> CRS-notatie (`EPSG:28992` vs OGC-URI) verschillen per DSO-deel-API."*

> **API-contract** — *"Gegokte endpoints, headers en veldnamen kloppen zelden; de OpenAPI-spec plus een
> live call zijn nodig vóór het bouwen."*

**Wat er onder de motorkap gebeurt.** Let op het woord *"keer op keer"*. Dit is niet één keer misgegaan.
Dezelfde mensen zijn in dezelfde valkuil gelopen bij verschillende use-cases, en pas toen het als patroon
werd opgeschreven, ging het de volgende keer sneller.

**Signaal in je eigen werk:** heeft jouw organisatie zo'n lijst? Niet een lijst met incidenten, maar met
patronen — dingen die meer dan één keer misgingen. Als die er niet is, wordt elke fout opnieuw ontdekt.

**Wat je checkt:** vraag naar de laatste drie technische problemen bij een koppeling. Zit er een patroon
in, en wist iemand dat vooraf?

---

## Proef 2 · Kwaliteit is geen cijfer

Kijk hoe de kwaliteitsaspecten geformuleerd zijn. Nergens staat een rapportcijfer of een stoplicht.

Wel staan er zinnen als: *"Kalibratie dBFS→dB(A) tegen een referentie-SLM nodig; publieke locatie bewust
afgerond (privacy)."*

**Wat er onder de motorkap gebeurt.** Dat is één zin met drie dingen erin: wat er niet klopt, waarom het
niet erger is dan het lijkt, en welke keuze bewust gemaakt is. Een stoplicht had daar "oranje" van
gemaakt, en dan was alle informatie weg.

**Signaal in je eigen werk:** dashboards met stoplichten per databron zien er beheersbaar uit en zeggen
zelden iets. De vraag is niet "is deze bron groen" maar "wat weet ik wel en niet over deze bron".

**Wat je checkt:** kun je bij een bron die als "goed" te boek staat, opnoemen wat er níet aan klopt? Zo
niet, dan heeft niemand gekeken — een bron zonder bekende beperkingen is een bron die niet onderzocht is.

---

## Proef 3 · De cijfers achter één laag

Open `/wfs-kwaliteit`. Deze pagina scant een landelijk register en telt.

Uit de scan van 3 september 2026, steekproef van 300 objecten per laag:

| laag | objecten | ongeldige geometrie |
|---|---:|---:|
| `bl_pr10_6` | 52.913 | **94,3 %** |
| `bl_gifwolkaandachtsgebieden` | 37 | **91,9 %** |
| `ev_referenties_polygon` | 21.842 | 67,7 % |
| `kgl_public` | 6.305.053 | 39,7 % |

En vier velden die het informatiemodel voorschrijft — `bronhoudercode`, `bevoegdgezag`,
`begin_geldigheid`, `tijdstip_registratie` — zitten niet in het schema van de laag.

**Wat er onder de motorkap gebeurt.** Dit is geen kritiek op de beheerder van dat register. Het is wat een
geautomatiseerde controle vindt als iemand hem uitvoert. Het punt van deze pagina is dat zo'n controle
bestaat en herhaalbaar is — niet dat de uitkomst slecht is.

**Signaal in je eigen werk:** wordt er ooit geteld? Niet "is de koppeling actief", maar hoeveel objecten
er binnenkomen en hoeveel daarvan bruikbaar zijn.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De asvolgorde is drie keer opnieuw ontdekt**, in verschillende use-cases, door dezelfde mensen. Pas na
  de derde keer stond het als patroon genoteerd.
- **De eerst gekozen collection was bijna leeg.** De gegevens bleken over zes collections verdeeld en juist
  de logisch klinkende was nauwelijks gevuld. Er kwam geen foutmelding; er kwamen weinig resultaten, en
  weinig ziet eruit als een geldig antwoord.
- **Een ongeldige bounding box gaf een 500 in plaats van een 400.** Een serverfout waar een invoerfout
  hoorde te staan, waardoor je de verkeerde kant op gaat zoeken.
- **De kwaliteitspagina zelf noemde het project maandenlang bij de oude naam.** Zichtbaar in de
  automatisch gegenereerde API-beschrijving. Uitgerekend de pagina over kwaliteit.

---

## Wat je hiervan meeneemt

| vraag over jouw bronnen | waarom |
|---|---|
| Bestaat er een lijst met terugkerende patronen? | anders wordt elke fout opnieuw ontdekt |
| Kun je van je belangrijkste bron zeggen wat er niet aan klopt? | "niets" betekent dat niemand keek |
| Wordt er geteld, of alleen gepingd? | een actieve koppeling kan lege data leveren |
| Wie schrijft op wat er misging, en leest iemand dat terug? | opschrijven zonder terugleze is archiveren |

**Volgende:** module L2 kijkt in de vergunningen-chatbot die je in K4 gebruikt hebt — van binnen.
