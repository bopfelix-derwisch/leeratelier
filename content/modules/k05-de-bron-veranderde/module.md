---
id: k05-de-bron-veranderde
titel: "De bron veranderde — en niemand zei iets"
spoor: basis
volgorde: 50
competenties: [B3]
duur_min: 30
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "signaallijst voor de eigen bron"
poc: leefomgevinglab
routes: ["/wfs-kwaliteit", "/api/wfs-kwaliteit", "/openapi.json"]
---

# De bron veranderde

De vorige module ging over een model dat iets fout zegt. Deze gaat over iets vervelenders: een keten waarin
niets stukgaat, geen foutmelding verschijnt, en het antwoord toch niet klopt — omdat de bron eronder
veranderde en niemand het merkte.

Deze module kost **geen modelbeurten**. Je kijkt naar echte data uit een landelijk register.

**Wat je nodig hebt:** je browser, en de kwaliteitspagina van LeefomgevingLab.

---

## Wat je gaat zien

| # | Wat er verandert | Wat je merkt |
|---|---|---|
| 1 | Het coördinatenstelsel | niets — de punten staan alleen ergens anders |
| 2 | De asvolgorde binnen dat stelsel | niets — noord en oost wisselen stilletjes |
| 3 | Velden die de specificatie voorschrijft | niets — ze zijn er gewoon niet |
| 4 | De inhoud zelf | niets — de laag is leeg of vol ongeldige vormen |

Vier keer "niets". Dat is de hele module.

---

## Proef 1 · Hetzelfde punt, drie plaatsen

Open **[`/wfs-kwaliteit`](https://leefomgevinglab.felixisfelix.com/wfs-kwaliteit)**. Deze pagina scant een landelijk register en rapporteert wat er over de data te
zeggen valt.

**Wat je doet:** zoek op welk coördinatenstelsel de lagen gebruiken, en vergelijk dat met wat je zou
verwachten.

**Wat er onder de motorkap gebeurt.** Nederland kent twee stelsels die je door elkaar kunt halen:

| | EPSG:28992 (RD New) | EPSG:4326 (WGS84) |
|---|---|---|
| eenheid | meters | graden |
| een punt in Utrecht | 136000, 456000 | 5.12, 52.09 |
| fout van 1 in de eerste waarde | 1 meter | ongeveer 70 kilometer |

Een getal als `5.12` is in RD een geldige coördinaat — hij ligt alleen in de Noordzee. Er komt dus geen
foutmelding, alleen een punt op de verkeerde plek.

**Wat de bouwers hier tegenkwamen**, letterlijk uit de kwaliteitspagina: *"Safety-kritisch: het
CQL-filter-punt wordt in de native CRS (RD/EPSG:28992) geïnterpreteerd — een lon/lat-punt geeft stil 0
treffers (vals-negatief)."*

Lees die laatste twee woorden nog eens. Je vraagt of er risicobronnen in de buurt zijn, je krijgt "nee",
en dat "nee" is fout. Geen foutmelding, geen lege pagina, geen waarschuwing. Gewoon nul.

**Signaal in je eigen werk:** een kaart waarop iets nét naast staat, of een zoekopdracht die opvallend
weinig oplevert.

**Wat je checkt:** vraag één bekend punt op — je eigen gemeentehuis — en kijk of het op de goede plek
staat. Dat is de hele test, en hij duurt een minuut.

---

## Proef 2 · De asvolgorde die niemand voorschrijft

Zelfs binnen één stelsel kan de volgorde van de twee getallen verschillen: eerst noord dan oost, of
andersom.

**Wat er onder de motorkap gebeurt.** De asvolgorde staat in de **definitie van het coördinatenstelsel**,
niet in de service die het levert. `EPSG:4326` schrijft lat,lon voor. Veel software levert lon,lat omdat
dat handiger is. Beide zijn te verdedigen; door elkaar gebruiken is dat niet.

Uit de kwaliteitspagina: *"De INSPIRE-laag levert EPSG:4258 met lat,lon-asvolgorde en negeert
`bbox-crs`."* Die service negeert dus de parameter waarmee je zegt in welk stelsel je bounding box staat.
Je vraagt netjes, hij luistert niet, en hij zegt er niets over.

En verderop: *"De `Content-Crs`-header moet de OGC-URI-vorm zijn
(`http://www.opengis.net/def/crs/EPSG/0/28992`); `EPSG:28992` geeft 400 — afwijkend van de
toepasbare-regels-API."* Twee onderdelen van hetzelfde stelsel, twee notaties voor hetzelfde stelsel.

**Signaal in je eigen werk:** alles staat gespiegeld over de diagonaal, of een gebied levert data uit een
heel andere provincie.

**Wat je checkt:** staat er in de documentatie welke asvolgorde geldt, en is dat getest met een punt
waarvan je het antwoord kent? "Het staat in de standaard" is geen test.

---

## Proef 3 · Velden die de specificatie eist maar die er niet zijn

Open **[`/wfs-kwaliteit`](https://leefomgevinglab.felixisfelix.com/wfs-kwaliteit)** en zoek de kolom met IMEV-velden.

> De ruwe cijfers staan achter `/api/wfs-kwaliteit`, maar die aanroep doet de scan opnieuw en duurt
> langer dan de tunnel toestaat. Gebruik de pagina, niet de API.

**Wat je ziet.** Vier velden die de informatiemodelspecificatie voorschrijft, ontbreken in het schema van
de laag:

```
bronhoudercode · bevoegdgezag · begin_geldigheid · tijdstip_registratie
```

**Wat er onder de motorkap gebeurt.** Dit zijn precies de velden waarmee je zou vaststellen *wie* deze
gegevens levert, *wie* er bevoegd gezag over is, en *sinds wanneer* ze gelden. Ze staan in de norm. Ze
staan niet in de data.

Een toepassing die deze laag gebruikt, kan dus niet tonen hoe oud een gegeven is of wie ervoor
verantwoordelijk is — niet omdat de bouwer dat vergat, maar omdat het er niet in zit.

**Signaal in je eigen werk:** een scherm waarop "laatst bijgewerkt" of "bron" leeg blijft, of helemaal
ontbreekt terwijl je het wel verwacht had.

**Wat je checkt:** vergelijk de velden in de geleverde data met de velden in de specificatie. Verschil is
normaal; wat je wilt weten is of iemand dat verschil kent.

---

## Proef 4 · De inhoud zelf

Kijk op **[`/wfs-kwaliteit`](https://leefomgevinglab.felixisfelix.com/wfs-kwaliteit)** naar de kolom met ongeldige geometrieën. Een greep uit de scan van
3 september 2026, steekproef van 300 per laag:

| laag | objecten | ongeldige vorm |
|---|---:|---:|
| `bl_pr10_6` | 52.913 | **94,3 %** |
| `bl_gifwolkaandachtsgebieden` | 37 | **91,9 %** |
| `ev_referenties_polygon` | 21.842 | 67,7 % |
| `bl_buisleidingreferentie` | 187.155 | 43,3 % |
| `kgl_public` | 6.305.053 | 39,7 % |
| `ev_activiteiten` | 29.294 | 5,3 % |

En drie lagen bevatten **nul objecten**, terwijl ze wel bestaan en netjes antwoorden.

**Wat er onder de motorkap gebeurt.** "Ongeldige geometrie" betekent bijvoorbeeld een vlak waarvan de rand
zichzelf kruist. Zulke vormen tekenen vaak gewoon op een kaart, maar berekeningen erop — ligt dit punt
erbinnen, hoe groot is het oppervlak — geven onbetrouwbare of stilzwijgend foute uitkomsten.

Een lege laag is nog stiller. Je vraagt of er aandachtsgebieden zijn, je krijgt een keurige lege lijst
terug, en die betekent "niet aanwezig in deze laag" — niet "niet aanwezig in de werkelijkheid".

**Signaal in je eigen werk:** een filter dat opeens veel minder oplevert dan vorige maand, of een laag die
al een tijd niets teruggeeft zonder dat iemand daarover belde.

**Wat je checkt:** hoeveel objecten hoort deze laag te bevatten, en hoeveel bevat hij nu? Eén getal, en
het verschil met vorige maand is het signaal.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **De eerst gekozen collection was bijna leeg.** Bij het bouwen van een use-case werd een collection
  gekozen die logisch klonk. Pas veel later bleek dat de gegevens over zes collections verdeeld zijn en dat
  juist de gekozene nauwelijks gevuld was. Er was geen foutmelding; er waren alleen weinig resultaten, en
  weinig ziet eruit als een geldig antwoord.
- **Een gegokt endpoint bestond niet.** Uit de kwaliteitspagina: *"Het gegokte operatie-pad bestond niet;
  de echte is `werkzaamheden/_bepaalRegelbeheerobjectTyperingen` (POST)."* De les die daar als terugkerend
  patroon staat: *"Gegokte endpoints, headers en veldnamen kloppen zelden; de OpenAPI-spec plus een live
  call zijn nodig vóór het bouwen."*
- **Een ongeldige bounding box gaf een 500 in plaats van een 400.** Een serverfout waar een
  invoerfout hoorde te staan. Wie dat ziet, gaat de server debuggen in plaats van zijn eigen aanroep.
- **De asvolgorde is drie keer opnieuw ontdekt.** In verschillende use-cases, door dezelfde mensen. Het
  staat nu als terugkerend patroon op de kwaliteitspagina, en dat is de enige reden dat het de vierde keer
  sneller ging.

Wat deze vier gemeen hebben: geen van alle veroorzaakte een storing. Alles bleef draaien, alles bleef
antwoorden, en de antwoorden waren fout.

---

## Wat je hiervan meeneemt

Het bewijsstuk van deze module is een **signaallijst voor je eigen bron**. Vier regels volstaan:

| Wat kan er veranderen | Waaraan zou ik het merken | Wat check ik dan |
|---|---|---|
| coördinatenstelsel of asvolgorde | iets staat nét naast, of een zoekopdracht levert niets | één bekend punt opvragen |
| veldnamen of ontbrekende velden | een schermveld blijft leeg | data vergelijken met de specificatie |
| aantal objecten in een laag | minder resultaten dan vorige maand | het aantal opvragen en vergelijken |
| endpoint of notatie | een aanroep die het altijd deed, doet het niet meer | de OpenAPI-spec naast de eigen aanroep |

De vraag die je uiteindelijk aan je leverancier stelt is deze: **wat gebeurt er in jullie systeem als de
bron verandert zonder dat iemand het meldt?** Als het antwoord "dan zien we dat vanzelf" is, vraag door
hoe.

**Volgende:** module K6 gaat over het draaiend houden van dit alles — en over wie er belt als het misgaat.
