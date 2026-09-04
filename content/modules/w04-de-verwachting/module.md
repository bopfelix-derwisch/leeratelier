---
id: w04-de-verwachting
titel: "De verwachting — veertien dagen vooruit, live"
spoor: waterlab
volgorde: 40
competenties: [B2, B3, B6]
duur_min: 35
beurten: 0
modellen: []
conserven: null
status: gepubliceerd
wat_ging_mis: true
bewijs: "de aannames achter een voorspelling in je eigen werk, benoemd"
poc: waterlab
routes: ["/api/forecast"]
---

# De verwachting

De andere modules van dit spoor spelen iets na dat al gebeurd is. Deze niet. De verwachting haalt op dit
moment live gegevens op, rekent veertien dagen vooruit, en zet er een alarmniveau bij.

Dat maakt hem de leukste om naar te kijken en de gevaarlijkste om te vertrouwen — en die twee hebben
dezelfde oorzaak.

Deze module kost **geen modelbeurten**. Alles wat je hier ziet is echt en van vandaag.

**[Open de verwachting](https://waterlab.felixisfelix.com/#forecast)** ·
**[de ruwe uitvoer](https://waterlab.felixisfelix.com/api/forecast)**

---

## Hoe het werkt

Drie bronnen, één rekenmodel, veertien dagen uitvoer.

| stap | wat er gebeurt | waar het vandaan komt |
|---|---|---|
| 1 | debiet Westervoort, 35 dagen terug | RWS Waterinfo |
| 2 | waterpeil Kampen, 35 dagen terug | RWS Waterinfo |
| 3 | officiële peilverwachting Kampen, 2–5 dagen | RWS Waterinfo, `proces_type: verwachting` |
| 4 | neerslag stroomgebied, 30 dagen terug + 14 vooruit | Open-Meteo |
| 5 | routering Westervoort → Kampen | **vaste vertraging van 2 dagen, factor 0,85** |
| 6 | recessie: hoe zakt het weg zonder regen | exponentieel naar een seizoensgemiddelde, tijdconstante 10 dagen |
| 7 | neerslagbijdrage | impulsresponsie, ongeveer 36 m³/s per mm per dag |
| 8 | onzekerheidsband | **een vaste formule, geen berekening** |
| 9 | alarmniveau | drempel 1500 m³/s |

Stap 5 tot en met 8 zijn het model. Het is geen hydrologisch model maar een **statistisch** model van
ruim honderd regels: het kent geen rivierbedding, geen dijken, geen stuwen. Het kent alleen hoe hard het
water er de afgelopen weken doorheen ging en hoeveel regen er verwacht wordt.

Dat is geen bezwaar. Het is wel iets dat je moet weten voordat je naar de grafiek kijkt.

---

## Proef 1 · De onzekerheidsband wordt niet berekend

Open de verwachting en kijk naar de grijze band om de lijn. Hij wordt breder naarmate je verder vooruit
kijkt. Dat klopt intuïtief: verder weg is onzekerder.

**Wat er onder de motorkap gebeurt.** De band komt uit één regel:

```python
unc = 0.18 + 0.04 * dag        # dag 1 tot en met 14
```

Achttien procent op dag één, vier procentpunt erbij per dag, dus **vierenzeventig procent op dag
veertien**. Dat is geen uitkomst van een berekening en het zegt niets over déze verwachting. Het is een
aanname over hoe onzeker een voorspelling ongeveer wordt, opgeschreven als formule.

Wat je vandaag ziet, met de cijfers van 4 september 2026:

| | ondergrens | midden | bovengrens |
|---|---:|---:|---:|
| dag 1 | 353 | 453 | 553 |
| dag 14 | 107 | 412 | 717 |

Op dag veertien loopt de band van 107 tot 717 m³/s — bijna een factor zeven. Dat is eerlijk breed, en het
is nog steeds geen meting van onzekerheid.

**Signaal in je eigen werk:** een onzekerheidsband die er bij elke voorspelling hetzelfde uitziet. Als de
band niet smaller wordt wanneer de invoer beter is, meet hij de invoer niet.

**Wat je checkt:** vraag hoe de band berekend wordt. Als het antwoord een formule met vaste getallen is,
is dat prima — mits het zo genoemd wordt en niet als "de onzekerheid van het model".

---

## Proef 2 · Het alarm kijkt naar de bovenkant

Er zijn vier niveaus: normaal, waakzaam, verhoogd, hoog. De drempel is 1500 m³/s.

**Wat er onder de motorkap gebeurt.** Het niveau wordt niet bepaald door de verwachte waarde maar door de
**bovenkant van de onzekerheidsband**:

```python
if peak_high >= 1500 * 1.5:  alert = "hoog"
elif peak_high >= 1500:      alert = "verhoogd"
```

`peak_high`, niet `peak_mid`. Dat is een bewuste keuze: bij hoogwater wil je liever te vroeg dan te laat
gewaarschuwd worden. Maar het betekent ook dat het alarm meeschaalt met een band die, zoals proef 1 liet
zien, uit een vaste formule komt. Een bredere band geeft eerder alarm, zonder dat er iets aan de
werkelijkheid veranderd is.

**Signaal in je eigen werk:** een drempel die op een afgeleide waarde staat in plaats van op een meting.
Dat is vaak verstandig, en het verdient een zin uitleg naast het getal.

**Wat je checkt:** waarop precies staat de drempel — de verwachting, de bovengrens, of de meting? En wie
heeft dat gekozen?

---

## Proef 3 · Wat er gebeurt als de bron wegvalt

Dit is de belangrijkste proef, en op dit moment is hij niet theoretisch.

**Wat je doet:** open [de ruwe uitvoer](https://waterlab.felixisfelix.com/api/forecast) en kijk in
`measured.q_westervoort` naar de laatste dagen.

**Wat er vandaag staat** (gemeten op 4 september 2026):

```
2026-08-28   71.4
2026-08-29   71.4
2026-08-30   71.4
2026-08-31  400.0
2026-09-01  400.0
2026-09-02  400.0
2026-09-03  400.0
2026-09-04  400.0
```

Vijf dagen achter elkaar exact 400,0. Een rivier doet dat niet.

**Wat er onder de motorkap gebeurt.** In de code staat `fillna(400.0)`: ontbreken er metingen, dan wordt
er een vaste waarde ingevuld. De laatste echte meting was **71,4 m³/s op 30 augustus**. Alles daarna is
opvulling.

En die opvulling is niet zomaar een gat in een grafiek. De verwachting begint bij de laatste waarde:

```python
q0 = q_west.iloc[-1]           # = 400.0
```

De hele veertiendaagse voorspelling vertrekt dus vanaf een getal dat niemand gemeten heeft, en dat bijna
zes keer zo hoog is als de laatste echte meting.

**En er staat geen enkele waarschuwing bij.** Het veld `data_available` staat op `true`, want er zaten
genoeg oude metingen in het venster. Het dashboard toont dat veld sowieso niet.

**Signaal in je eigen werk:** herhaalde identieke waarden. Een echte meetreeks heeft ruis; drie of vijf
keer exact hetzelfde getal betekent bijna altijd invulling, interpolatie of een vastgelopen sensor.

**Wat je checkt:** is er in de uitvoer te zien welke waarden gemeten zijn en welke ingevuld? Zo niet, dan
zie je het verschil alleen door de getallen zelf te bekijken — en dat doet vrijwel niemand.

---

## Proef 4 · Vergelijk met de officiële verwachting

Het dashboard legt de officiële RWS-verwachting van het waterpeil bij Kampen over de eigen berekening
heen. Die loopt twee tot vijf dagen vooruit; vandaag zijn het er drie.

**Kijk naar:** waar de twee lijnen uiteenlopen, en wat er gebeurt na dag vijf.

**Wat er onder de motorkap gebeurt.** Na dag vijf is er geen officiële verwachting meer en staat de eigen
lijn er alleen. Precies daar wordt de band het breedst en de onderbouwing het dunst, en precies daar kijkt
een gebruiker het liefst — want vandaag weet je toch al.

**Signaal in je eigen werk:** een grafiek waarin een betrouwbare en een indicatieve bron in dezelfde stijl
getekend worden. Als je aan de lijn niet ziet welke welke is, ziet niemand het.

**Wat je checkt:** is in de weergave zichtbaar waar de ene bron ophoudt en de andere doorloopt?

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **Op dit moment draait de verwachting op een opvulwaarde.** Sinds 31 augustus 2026 komen er geen
  metingen bij Westervoort binnen. De reeks wordt aangevuld met 400,0 m³/s, de verwachting vertrekt vanaf
  dat getal, en er staat nergens iets over. Dit is geen bedacht voorbeeld: het is wat er stond toen deze
  module geschreven werd, en je kunt het zelf nakijken.
- **`data_available` bestaat wel maar wordt niet getoond.** De API geeft het veld netjes mee. Het
  dashboard doet er niets mee. Een waarschuwing die alleen in de JSON staat, bereikt geen enkele gebruiker.
- **De vlag staat bovendien op `true` terwijl er vijf dagen ontbreken.** Hij kijkt of er minstens vijf
  metingen in het venster van 35 dagen zitten, niet of de recente dagen er zijn. Voor een verwachting die
  vanaf de laatste waarde vertrekt, is juist dat laatste wat telt.
- **De opvulwaarde is een rond getal.** Dat is de enige reden dat het opvalt. Was er met het
  seizoensgemiddelde opgevuld, dan had niemand het gezien.

---

## Wat er nog te doen is

Dit is een proefopstelling en de meeste hiervan zijn bewuste beperkingen, geen fouten. Ze staan hier zodat
je weet wat je wel en niet mag verwachten.

| wat | waarom het er nog niet is |
|---|---|
| **Ontbrekende metingen markeren in de weergave** | de gegevens zijn er (`data_available`, en de opvulwaarden zijn herkenbaar); het is een kwestie van tonen. Dit is de belangrijkste. |
| **`data_available` strenger maken** | nu telt hij metingen in 35 dagen; hij zou moeten kijken of de laatste dagen er zijn |
| **Opvullen met het seizoensgemiddelde in plaats van 400** | eerlijker getal, maar dan valt het niet meer op — dus liever markeren dan mooier opvullen |
| **De onzekerheidsband uit de gegevens afleiden** | bijvoorbeeld uit de spreiding van de neerslagverwachting, of uit hoe goed eerdere verwachtingen uitkwamen |
| **Terugkijken hoe goed het was** | er wordt niet bijgehouden of de verwachting van veertien dagen geleden klopte. Zonder dat kan niemand zeggen of dit model iets waard is |
| **Een hydrologisch model in plaats van een statistisch** | wflow draait al voor de casussen; het is niet gekoppeld aan de live verwachting |

Die vijfde is de interessantste. Er is nu geen enkele manier om te weten of deze verwachting goed is,
want er wordt niet nagerekend. Module W3 gaat over wat validatie bewijst; hier is er domweg geen.

---

## Wat je hiervan meeneemt

| vraag over een voorspelling in jouw werk | waarom |
|---|---|
| Waar komt de onzekerheidsband vandaan? | een vaste formule is prima, mits hij zo genoemd wordt |
| Staat het alarm op de verwachting of op de bovengrens? | allebei verdedigbaar, maar het moet ergens staan |
| Is te zien welke invoerwaarden gemeten zijn en welke ingevuld? | dit is het verschil tussen een verwachting en een gok |
| Wordt achteraf nagerekend of het klopte? | zonder dat weet niemand of het model iets toevoegt |
| Wat gebeurt er als de bron een week stilvalt? | het antwoord is vaak "dan rekent hij gewoon door" |

De laatste vraag is de vraag van deze hele module. Een systeem dat stopt als de data uitvalt, is
irritant. Een systeem dat doorrekent alsof er niets aan de hand is, is gevaarlijk — en het ziet er
precies hetzelfde uit als een systeem dat werkt.

**Volgende:** je hebt spoor W nu gehad. Als je de basisroute nog niet af hebt, ga dan naar K7 en vul je
beheerkaart in — de vragen hierboven passen er rechtstreeks in.
