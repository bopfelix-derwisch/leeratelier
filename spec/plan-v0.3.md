# Leeratelier — plan en spec v0.3

> **Vervangt v0.2.** Alle veertien openstaande vragen zijn beantwoord. De doelgroep is opnieuw verschoven —
> van architecten naar **functioneel beheerders en technisch geïnteresseerden** — en dat verandert de inhoud
> ingrijpender dan de techniek. Startdocument voor Claude Code.

## Wat er veranderd is t.o.v. v0.2

| | v0.2 | v0.3 (besloten) |
|---|---|---|
| Doelgroep | architecten en technisch leiders | **functioneel beheerders + technisch geïnteresseerden** |
| Eindproduct deelnemer | architectuurnotitie | **beheerkaart voor de eigen toepassing** |
| Openingstijden | dagvenster | **permanent open** |
| Toegang | e-mail-OTP | **alles onder inlog** |
| Bouwvolgorde | eerst één module, dan portaal | **eerst het volledige raamwerk (dun), dan één module volledig, dan incrementeel** |
| Domein | één route | **basisroute + spoor Waterlab + spoor LeefomgevingLab** |
| Modellen | één klasmodel | **modellenbank: meerdere modellen naast elkaar** |
| Logging | opt-in | **vragen worden gelogd** |
| Begeleiding | maandelijkse sessie (open vraag) | **ja, jij begeleidt die** |

---

## 1. Visie

**Ik wil het vak van informatieprofessional op een nieuwe manier vormgeven met AI. En ik wil dat dat
leerproces concrete initiatieven op gang brengt: met nieuwe instrumenten leren spelen in hetzelfde orkest.**

Het orkest is het stelsel — DSO, BALO, bronhouders, wetgeving, vakgemeenschap. Dat verandert niet. De
partituur — wet, standaarden, datamodellen — blijft leidend. De nieuwe instrumenten zijn LLM, embeddings,
RAG, lokale inferentie. Het atelier is de repetitieruimte; het optreden is wat de bezoeker daarna in de
eigen organisatie doet.

BluesLab is die metafoor letterlijk in code: hetzelfde stuk, getransponeerd naar Bes-klarinet en alt-sax,
met concert pitch als interne representatie. Eén betekenis, meerdere instrumenten, één canonieke vorm
eronder.

### Waarom functioneel beheerders de juiste eerste doelgroep zijn

Architecten beslissen over AI; functioneel beheerders **leven ermee**. Zij krijgen de vraag "waarom zegt
dat ding dit?", zij merken als eerste dat een bron veranderd is, zij moeten uitleggen aan gebruikers wat
er misging, en zij bellen de leverancier. Zij zijn ook degenen van wie de organisatie het minst verwacht
dat ze hier verstand van hebben — en dat is precies waarom hier het meeste te winnen valt.

Deze doelgroep heeft geen behoefte aan architectuurkeuzes. Ze hebben behoefte aan **grip**: weten wat er
onder de motorkap gebeurt, herkennen wanneer een antwoord niet klopt, en weten wat ze moeten checken als
het misgaat.

**Belofte:** *Je weet daarna wat er in een AI-toepassing gebeurt, je herkent wanneer het antwoord niet
deugt, en je gaat weg met een beheerkaart voor je eigen toepassing.*

**Anti-belofte:** geen programmeren, geen architectuurdocumenten, geen leverancierskeuze, geen installatie
op je eigen laptop.

---

## 2. Interactieniveau 1

**Wel:** publieke pagina's doorlopen · de chatbots bevragen · `/openapi.json` bekijken · een `curl`-voorbeeld
kopiëren en de respons zien · dezelfde vraag aan meerdere modellen stellen met tijd en geheugen ernaast ·
een beheerkaart invullen en meenemen.

**Niet:** code wijzigen · eigen omgeving opzetten · installeren · SSH naar orin3 · iets in een repo veranderen.

**Browser-only is een harde eis.** Bij overheidsorganisaties is "ik mag niets installeren" de regel. Een
atelier dat werkt zonder installatie bereikt juist de doelgroep die anders afhaakt.

---

## 3. Competentieprofiel — functioneel beheer met nieuwe instrumenten

| # | Competentie | Bewijsstuk |
|---|---|---|
| **B1** | **Onder de motorkap kijken.** Kan benoemen uit welke onderdelen een AI-toepassing bestaat — model, embeddings, index, prompt, bron — en wat elk doet. | invulschema van één POC |
| **B2** | **Een antwoord wantrouwen.** Herkent de faalvormen: verzonnen bron, verouderde index, te streng contract dat nuttige informatie onderdrukt, plausibel maar fout. | drie zelf gevonden foute antwoorden, met diagnose |
| **B3** | **Bronveranderingen zien aankomen.** Weet wat er misgaat als een bron verandert — coördinaatstelsel, veldnaam, endpoint, leeggelopen collection — en wat dan te doen. | signaallijst voor de eigen bron |
| **B4** | **Beheerlast inschatten.** Weet wat een AI-toepassing kost aan onderhoud: index verouderen, modellen, degradatie, monitoring, wie er belt als het stukloopt. | beheerkaart (zie hieronder) |
| **B5** | **De juiste vraag stellen.** Kan doorvragen bij leverancier of bouwer tot duidelijk is wat er werkelijk gebeurt. | vragenlijst van tien vragen aan de eigen leverancier |
| **B6** | **Oordeelsvorming.** Benoemt waar het model het denken ondersteunt en waar het het overneemt. | slotalinea op de beheerkaart |

**Verplicht: B2, B3 en de beheerkaart.** De rest is aanbevolen.

### De beheerkaart — het eindproduct

Eén A4 over de eigen toepassing of bron. Dit vervangt de architectuurnotitie uit v0.2 en past veel beter
bij het dagelijks werk van deze doelgroep:

1. **Wat gaat hier het eerst mis?** — drie realistische faalvormen
2. **Waaraan merk ik het?** — het signaal per faalvorm, niet de oorzaak
3. **Wat check ik dan?** — concrete handeling, uitvoerbaar zonder ontwikkelaar
4. **Wanneer is het niet meer mijn probleem?** — escalatiepunt en aan wie
5. **Wat vraag ik mijn leverancier de eerstvolgende keer?** — drie vragen
6. **Waar neemt het model het denken over?** — één alinea

Concreet, meeneembaar, en meteen bruikbaar in het eigen team. Dit is de "concrete impuls" uit je visie in
zijn kleinste werkbare vorm.

---

## 4. Toegang, capaciteit en permanent bedrijf

### 4.1 Alles onder inlog

Advies: **Cloudflare Access met e-mail-OTP**. Geen accounts bouwen, geen wachtwoorden beheren, wel een
identiteit per bezoeker — nodig voor het persoonlijke budget en voor de logging. De tunnel is al
dashboard-managed, dus dit is configuratie, geen code.

### 4.2 Permanent open = onbewaakt bedrijf

Dit is de grootste consequentie van je keuze. Permanent open, terwijl jij niet altijd bereikbaar bent,
betekent dat het atelier **zonder ingrijpen moet blijven werken**. Ontwerpeisen:

- alle units `Restart=always` met watchdog; klasmodel draait permanent, niet per dag gestart
- de bemiddelaar overleeft het wegvallen van een model: verkeer valt terug op de degradatieladder
- **conserven maken de hele route beschikbaar zonder enig model** — dat is niet de noodrem maar een
  volwaardig pad
- dagbudget reset automatisch om middernacht
- storingsbanner op het portaal, automatisch gezet door sysmonitor
- eerlijke verwachting op de inlogpagina: *dit is een privé-lab van één persoon; storingen kunnen dagen duren*

Die laatste regel is geen zwaktebod. Verwachtingsmanagement is het goedkoopste beheersinstrument dat er is,
en voor deze doelgroep is het meteen een les.

### 4.3 Rantsoeneer het model, niet de deur

De meeste leerwinst kost het model niets. Iemand die `/kwaliteit` leest, een WFS-call doet en de CRS-valkuil
ziet, belast alleen FastAPI. Alleen **modelbeurten** zijn schaars.

| | Licht pad | Zwaar pad |
|---|---|---|
| Wat | pagina's, dashboards, viewers, live API-calls, conserven | live LLM/RAG-antwoorden |
| Kosten | verwaarloosbaar | tientallen seconden, bandbreedtegebonden |
| Limiet | ~50 gelijktijdig | **dit rantsoeneer je** |

**Degradatieladder** (niemand krijgt "nee"):
1. cache-treffer → direct
2. klasmodel → snel, kleiner model, zichtbaar gelabeld
3. showmodel → traag, gerantsoeneerd
4. conserven → voorberekend, gemarkeerd; ook de uitwijk bij storing
5. budget op → licht pad blijft open, live antwoorden weer beschikbaar na middernacht

### 4.4 Budget als configuratie, niet als besluit

Je koos voor incrementeel bouwen. Zet het budget dus **niet vast in het plan maar in een configuratiebestand**,
met deze startwaarden, en stel ze bij na de ijking (WP-01):

```yaml
dagbudget_modelbeurten: 150
per_bezoeker_per_dag: 15
gereserveerd_begeleide_sessie: 0.20
gelijktijdig_klasmodel: 4
gelijktijdig_showmodel: 1
```

Waarom dit ordegrootte klopt: de keten is ~50–70 s bij koude cache en sequentieel. Eén slot bij 60 s per
antwoord en 40% belasting geeft ruwweg 190 antwoorden per dag; een sneller klasmodel en cache-treffers
vermenigvuldigen dat. Dat is een berekening uit je eigen inventarisgetallen, **geen meting** — vandaar WP-01.

### 4.5 Logging

Besloten: vragen worden gelogd. Ontwerp:

| Veld | Doel |
|---|---|
| bezoeker-id, tijdstip, module | zien waar mensen vastlopen |
| vraag, model, antwoordbron (cache/klas/show/conserf) | conserven en cache verbeteren |
| latency, verbruikte beurten | budget ijken |

Bewaartermijn **90 dagen**, gelijk aan `history.jsonl` van sysmonitor. Doel en termijn staan op de
inlogpagina. Dit is meteen materiaal voor module K6: iemand die zelf gelogd wordt, begrijpt beter waarom
logging in de eigen toepassing nodig is — en wat ervoor geregeld moet zijn.

### 4.6 Vastgelopen? — asynchrone begeleiding

Jij bent het contactpunt maar niet altijd bereikbaar. Dus per module een **"ik kom er niet uit"-knop** die:
1. direct de conserven en een uitlegkaart toont (zelfhulp eerst),
2. een melding wegschrijft met context: module, vraag, model, foutmelding, budgetstand,
3. de bezoeker een realistische reactietermijn toont.

Dat lost 80% zonder jou op, en de meldingen die overblijven zijn meteen bruikbaar als input voor de
volgende module.

---

## 5. Modellen — onderzoek en advies

Je vroeg om onderzoek naar andere modellen en om meerdere modellen naast elkaar. Onderzocht in september 2026.

### 5.1 Eerst de hardware-werkelijkheid

Tokengeneratie op deze machine is **geheugenbandbreedte-gebonden**, niet rekenkracht-gebonden. Ruwweg geldt:
tokens/s ≈ bandbreedte ÷ modelgrootte. Op een AGX Orin 64GB (~200 GB/s) betekent dat:

| Model | Q4-grootte | Theoretisch plafond | Realistisch |
|---|---|---|---|
| 32B (huidig showmodel) | 19 GB | ~10 tok/s | ~5–8 tok/s |
| 27B | ~17 GB | ~12 tok/s | ~6–9 tok/s |
| 12B | ~7 GB | ~28 tok/s | ~12–18 tok/s |
| 8B | ~5 GB | ~40 tok/s | ~15–25 tok/s |
| 4B | ~2,5 GB | ~80 tok/s | ~30–45 tok/s |

**Dit verklaart je 50–70 s ketenlatency volledig** — en het is precies de les van module K3. Het unified
memory van de Orin betekent dat modellen tot ~40 GB volledig op de GPU kunnen draaien; de beperking is
snelheid, niet of het past. Q4_K_M is voor Jetson de gangbare keuze: Q8 is te groot, Q2 kost te veel kwaliteit.

### 5.2 ⚠ Kritieke vondst: MoE hangt op deze chip

Er is een gemelde llama.cpp-bug waarbij **Mixture-of-Experts-modellen op Jetson Orin AGX (SM87, compute
capability 8.7) blijven hangen bij decode**, op alle builds ná b7309 (december 2025). Het model laadt, maar
er komen geen tokens. Getest met onder meer Qwen3-Coder-30B-A3B en GLM-4.7-Flash; dense modellen waren niet
getroffen.

*Bron: github.com/ggml-org/llama.cpp issue #19219 (januari 2026).*

**Jouw build is 8117 (b908baf18) — ruim ná b7309.** Dat is belangrijk, want juist de MoE-modellen zijn op
papier ideaal voor deze machine: Gemma 4 26B-A4B laadt ~15 GB maar activeert slechts ~3,8B parameters per
token, dus je krijgt de snelheid van een 4B-model bij de kwaliteit van iets veel groters. Precies wat een
bandbreedtegebonden machine nodig heeft.

De melding is van januari 2026 en kan inmiddels opgelost zijn. **WP-02 is: verifiëren voordat je erop plant.**

### 5.3 Kandidaten

| Model | Q4 | Licentie | Waarom | Let op |
|---|---|---|---|---|
| **Qwen3.x 8B-klasse** | ~5 GB | Apache 2.0 | Qwen heeft veruit de breedste meertaligheid (Qwen3.5: 201 talen). Voor Nederlands de sterkste kandidaat in deze maat. | versienamen wisselen snel — controleer welke variant als GGUF beschikbaar is |
| **Qwen3.6-27B / Qwen3.8-27B** | 17–24 GB | Apache 2.0 | beste kwaliteit-per-GB onder de dense modellen; directe opvolger van je huidige 32B | net zo bandbreedtegebonden als nu |
| **Gemma 4 12B** | ~7 GB | Apache 2.0 | Google heeft Gemma 4 naar plain Apache 2.0 gebracht; multimodaal incl. audio; lange context | trainings­nadruk Engels-centrischer → zwakker Nederlands |
| **Gemma 4 26B-A4B (MoE)** | ~15 GB | Apache 2.0 | op papier **de** Jetson-kandidaat: 4B-snelheid, 26B-kwaliteit | ⚠ zie §5.2 |
| **Gemma 4 E2B / E4B** | 2–3 GB | Apache 2.0 | echt klein en snel, goed contrastmateriaal | te licht voor NL-beleidstaal |
| **gpt-oss-20b** | ~16 GB | Apache 2.0 | redeneren binnen 16 GB | text-only |
| **Phi-4-mini** | <4 GB | MIT | lange context bij minimaal geheugen | zwak in het Nederlands |
| **Mistral-Nemo 12B** (staat er al) | 7 GB | Apache 2.0 | Europees, redelijk Nederlands, nul downloadtijd | oudere generatie |

**Over Nederlands:** ga niet op zoek naar een Nederlands model. Het Fietje-onderzoek laat zien dat kleine
meertalige modellen inmiddels Nederlands-specifieke modellen voorbijstreven. Kies dus op meertaligheid —
en daar is de Qwen-familie het sterkst.

### 5.4 Advies

- **Klasmodel (permanent op :8081):** een dense **Qwen3.x in de 8B-klasse**, Q4_K_M. Snel genoeg om
  interactief te voelen, Apache 2.0, en Nederlands is hier de doorslaggevende factor.
- **Showmodel (:8080):** houd Qwen2.5-32B voorlopig. Vervangen door Qwen3.6-27B is een verbetering maar
  niet blokkerend — doe het na de eerste module, niet ervoor.
- **Modellenbank (module K3):** vergelijk **vijf** modellen — E4B-klasse, 8B, 12B, 27B/32B en één MoE als
  §5.2 dat toelaat. Alleen twee daarvan draaien live; de andere drie komen **uit conserven**, offline
  voorberekend. Zo krijg je een vijfvoudige vergelijking zonder vijf modellen tegelijk te draaien.
- **Uit te zoeken:** of de MoE-bug nog speelt. Als die opgelost is, is Gemma 4 26B-A4B waarschijnlijk het
  beste dat deze machine kan draaien.
- **Te overwegen bij veel gelijktijdig bezoek:** vLLM voor het klasmodel. Op AGX Orin vraagt vLLM meer
  geheugenruimte dan llama.cpp maar verdient dat terug bij het bedienen van meerdere clients tegelijk.
  llama.cpp blijft dan voor het showmodel. Niet doen vóór WP-01 uitwijst dat het nodig is.

### 5.5 De ijkset — hoe je kiest is zelf de les

Bouw `ops/ijkset-nl.jsonl`: **twintig vaste vragen in het Nederlands uit je eigen domein** — vergunningen,
geluid, externe veiligheid, waterstand. Elk kandidaat-model beantwoordt ze; je legt tijd, geheugen en
antwoord naast elkaar.

Dat is tegelijk je selectieprocedure, je conserven-voorraad én het complete lesmateriaal van module K3.
Eén stuk werk, drie opbrengsten. Bouw dit vroeg.

---

## 6. De route

Besloten: incrementeel, met de sporen Waterlab en LeefomgevingLab als eigen plek.

### Basisroute (voor iedereen)

| # | Module | Kern | Beurten |
|---|---|---|---|
| **K1** | **Rondgang** | dertien dingen op één machine: wat draait er, wat kost het, wat is stuk | 0 |
| **K2** | **De motorkap zonder mystiek** | model, embeddings, index, prompt, bron — wat is wat en wat doet wat | 2 |
| **K3** | **De modellenbank** | dezelfde Nederlandse vraag aan vijf modellen, met tijd en geheugen ernaast | 2 live + conserven |
| **K4** | **Wanneer klopt het niet** | faalvormen live: verouderde index, verzonnen bron, te streng contract, plausibel maar fout | 3 |
| **K5** | **De bron veranderde** | RD vs WGS84, asvolgorde, genegeerde `bbox-crs`, leeggelopen collection | 0 |
| **K6** | **Draaiend houden** | sysmonitor, index-leeftijd, degradatie, logging, wie belt er | 0 |
| **K7** | **Je eigen beheerkaart** | invullen en meenemen | 0–2 |

### Spoor W · Waterlab

| # | Module | Kern |
|---|---|---|
| **W1** | **Een vakinterface nabouwen** | de FEWS PI-REST-emulatie: waarom dit prikkelt, en waarom het gevaarlijk is |
| **W2** | **Toen het misging** | de synthetische inflow en waarom de bronnen faalden |
| **W3** | **Casussen** | hoogwater 1995, droogte 2018, juli 2021, BRO-grondwaterkoppeling |

**Over W1 — je noemde het zelf "wat gevaarlijk maar wel prikkelend", en dat klopt.** Een nagebouwd
vakinterface waar bestaande clients op passen, is een prachtig patroon én een reële valkuil: het wekt de
indruk van een operationele dienst die het niet is, en het schept verwachtingen over beschikbaarheid en
correctheid die een proeftuin niet kan waarmaken. Voor functioneel beheerders is dat geen bezwaar maar
**het beste lesmateriaal op de hele machine**: dit is precies de situatie waarin zij straks moeten uitleggen
waarom iets eruitziet als de echte dienst en het niet is. Zet de waarschuwing in de module zelf, niet in
een voetnoot.

### Spoor L · LeefomgevingLab

| # | Module | Kern |
|---|---|---|
| **L1** | **Kwaliteit per POC** | de zes categorieën en "wat steeds terugkomt" |
| **L2** | **De vergunningen-chatbot van binnen** | RAG: chunks, embeddings, index, wat er gebeurt bij een vraag |
| **L3** | **Het antwoordcontract** | disclaimer, vangnet, degradatie — en waarom té streng ook fout is |

### Mislukking als doorlopend element

Besloten: ja, en prominent. Maak het **structureel** in plaats van een module: elke module krijgt een vaste
sectie **"wat hier misging"**, gevuld met de echte lessen — het gegokte endpoint dat niet klopte, de
INSPIRE-laag met lat,lon-asvolgorde, de collection die bijna leeg bleek, de ongeldige bbox die een 500 gaf
in plaats van een 400, de synthetische inflow die faalde.

Voor functioneel beheerders is dit het waardevolste deel van het hele atelier. Zij zien in hun werk alleen
de gepolijste eindproducten van leveranciers; hier zien ze wat eronder zit.

---

## 7. Tegenspraak: de maandelijkse sessie

Besloten: jij begeleidt een maandelijkse sessie. Vorm:

**Twee uur, zes deelnemers, gereserveerde capaciteit (20% van het dagbudget).** Toelating: je hebt de
basisroute gedaan en je beheerkaart meegebracht. De sessie is geen les maar **tegenspraak** — zes mensen
die elkaars beheerkaart aanvallen, met de POC's als bewijsmateriaal binnen handbereik.

Dit is het enige moment waarop een ingevulde kaart een besluit wordt. Zonder deze sessie levert het atelier
kennis op en geen initiatieven — de tweede helft van je visie hangt hieraan.

---

## 8. Architectuur

```
        bezoeker (browser, geen installatie)
                    │  Cloudflare Access (e-mail-OTP)
                    ▼
   ┌──────────────────────────────────────────────────────┐
   │ atelier-portaal  :8793                               │
   │  ├ routerenderer (modules uit markdown)              │
   │  ├ budgetmeter ("nog 9 beurten vandaag")             │
   │  ├ "ik kom er niet uit"-knop met contextvangst       │
   │  ├ beheerkaart K7 (invullen + exporteren)            │
   │  ├ metingenpaneel (tijd/geheugen bij K3)             │
   │  └ storingsbanner (gezet door sysmonitor)            │
   └───────────────┬──────────────────────────────────────┘
                   ▼
   ┌──────────────────────────────────────────────────────┐
   │ leerbemiddelaar  :8794                               │
   │  wachtrij · dag- en persoonsbudget · cache ·         │
   │  conserven · degradatieladder · logboek (90 dgn)     │
   └────────┬─────────────────────────────┬───────────────┘
            ▼                             ▼
   POC's (ongewijzigd)          AI-runtime
   :8792 leefomgevinglab        :8080 showmodel (32B, llama.cpp)
   :8000 waterlab               :8081 klasmodel (8B, permanent)  NIEUW
   :8788 morele-helper          :8082 bge-m3 embeddings
   :8795 sysmonitor
```

Poorten **8793/8794 vrij**; **8081 leeg** sinds `derwisch_local-nemo` disabled is.

**Dunne laag naast de POC's, niet erin.** Op niveau 1 raakt geen bezoeker ooit een POC-repo aan.

### Modules als bestanden

```yaml
---
id: k04-wanneer-klopt-het-niet
titel: "Wanneer klopt het antwoord niet?"
spoor: basis                # basis | waterlab | leefomgeving
competenties: [B2, B3]
duur_min: 30
beurten: 3
modellen: [klas, show]
conserven: conserven/k04.json
status: gepubliceerd        # concept | gepubliceerd
wat_ging_mis: true          # verplichte sectie
bewijs: "drie foute antwoorden met diagnose"
---
```

Het veld `beurten` reserveert budget vóórdat iemand aan de module begint, zodat niemand halverwege
zonder budget valt. Het veld `status` maakt incrementeel publiceren mogelijk: de route werkt met drie
modules net zo goed als met dertien.

### Sysmonitor-uitbreiding

Zelfde patroon als bestaand: elke warn/crit krijgt een concrete actie via `advise()`.

| Signaal | warn | crit | Actie |
|---|---|---|---|
| Dagbudget verbruikt | 70% | 90% | standaard naar klasmodel |
| Wachtrijdiepte | 4 | 8 | terugvallen op conserven |
| p95 antwoordlatency | 60 s | 120 s | showmodel uit de route |
| Leeftijd RAG-index | 30 d | 90 d | herbouwen |
| Klasmodel niet actief | — | direct | unit :8081 herstarten |
| Openstaande "vastgelopen"-meldingen | 3 | 10 | mail naar beheerder |

---

## 9. Ontwikkelvolgorde

Je koos: **volledig raamwerk eerst, dan de eerste module volledig, dan incrementeel.** Dat is het
"wandelend skelet": een dunne maar complete keten van inlog tot antwoord, bewezen met één echte module.

### Fase 0 · Fundament — blokkerend, ±1 week
- LICENSE in alle 9 repo's (advies: Apache-2.0; EUPL-1.2 als aansluiting bij overheidsbeleid zwaarder weegt)
- `docuchat`, `transcribe`, `sysmonitor` in git
- TLS: hernoem `admin.helper.` → `helper-admin.felixisfelix.com`
- API-titel `Geluidsmeter API` → `LeefomgevingLab API`
- dubbele belegging apex oplossen; geheimencheck (`.env`, `location_private.yaml`, Studio-PIN)

**Poort:** elke route die in een module voorkomt laadt, en elke repo heeft een licentie.

### Fase 1 · IJking, ijkset en modelkeuze
Meten wat de machine werkelijk aankan, de Nederlandse ijkset bouwen, het klasmodel kiezen, en de MoE-vraag
uit §5.2 beantwoorden.

**Poort:** een gemeten dagbudget, een gekozen klasmodel, en twintig ijkvragen met antwoorden van minstens
drie modellen.

### Fase 2 · Wandelend skelet — het volledige raamwerk, dun
Inlog → portaal → route → één dummy-module → bemiddelaar → budget → klasmodel → conserven → logging →
sysmonitor → "vastgelopen"-knop. Alles aanwezig, niets diep.

**Poort:** een testbezoeker logt in, doorloopt een module, verbruikt budget, krijgt bij uitputting een
conserf, en jij ziet dat terug in het logboek.

### Fase 3 · Eerste module volledig
**K4 "Wanneer klopt het niet"** volledig uitwerken. Dit is de kernmodule voor deze doelgroep en hij
belast de hele keten: RAG, twee modellen, conserven, logging.

Direct daarna **K1 en K5** toevoegen — die kosten nul modelbeurten en geven je vrijwel gratis een route
van drie modules die als geheel aanvoelt.

**Poort:** drie functioneel beheerders lopen K1–K4–K5 zonder hulp door en leveren de bewijsstukken van B2/B3.

### Fase 4 · Incrementeel uitbreiden
In deze volgorde: K6 → K7 beheerkaart → K3 modellenbank → K2 → spoor L → spoor W. Steeds één module,
steeds meteen live.

### Fase 5 · Openstellen en tegenspraak
Breder openzetten, eerste maandelijkse sessie draaien, runbook af.

**Poort:** ≥ 6 bezoekers hebben een beheerkaart afgerond en ≥ 3 daarvan hebben hem in het eigen team
besproken. *Hierop wordt de tweede helft van de visie afgerekend.*

---

## 10. Werkpakketten voor Claude Code

| WP | Fase | Taak | Klaar als |
|---|---|---|---|
| **WP-00** | 0 | Fundament: licenties, drie repo's in git, TLS-hernoeming, API-titel, geheimencheck | fase 0-poort gehaald |
| **WP-01** | 1 | **IJkmeting.** p50/p95 en tok/s op :8080 bij 1/2/4/8 gelijktijdige verzoeken; geheugen voor en na; rapport naar `ops/ijking/`; dagbudget eruit afleiden | reproduceerbaar rapport, budget in `config/budget.yaml` |
| **WP-02** | 1 | **MoE-verificatie.** Test of MoE-decode hangt op deze build (issue ggml-org/llama.cpp#19219, SM87, builds na b7309). Test met één MoE-GGUF; bij hangen: check of er een fix is of pin een werkende build | schriftelijk ja/nee met bewijs |
| **WP-03** | 1 | **Nederlandse ijkset** `ops/ijkset-nl.jsonl`: 20 domeinvragen; script dat elk kandidaat-model erlangs haalt en tijd/geheugen/antwoord wegschrijft | matrix van ≥3 modellen × 20 vragen |
| **WP-04** | 1 | Klasmodel als permanente systemd-unit op :8081, `Restart=always`. Let op: `--ctx-size` is het **totaal** en wordt over de slots verdeeld — bij `--parallel 4` minimaal 16384 | unit active na reboot; geheugen binnen grens |
| **WP-05** | 2 | Bemiddelaar :8794: wachtrij, dag- en persoonsbudget, cache op genormaliseerde prompt + module-id, conserven, degradatieladder §4.3, logboek met 90 dagen bewaartermijn | 8 gelijktijdige verzoeken, geen stilte, budget klopt |
| **WP-06** | 2 | Portaal :8793: routerenderer op de frontmatter uit §8, budgetmeter, "vastgelopen"-knop met contextvangst, storingsbanner | dummy-module draait end-to-end |
| **WP-07** | 2 | Cloudflare Access met e-mail-OTP op portaal en bemiddelaar; privacytekst over logging op de inlogpagina | alleen geverifieerde bezoekers; budget aan persoon gekoppeld |
| **WP-08** | 2 | Sysmonitor-uitbreiding met de zes drempels uit §8, inclusief `advise()`-teksten en het zetten van de storingsbanner | zichtbaar op statuspagina en in `history.jsonl` |
| **WP-09** | 2/3 | **RAG-index: eerst inspecteren, dan herbouwen.** `vectors.npy` is 33 KB; bij bge-m3 (1024 dim) is dat grofweg 8 chunks fp32. Lees vorm en dtype uit vóór je iets herbouwt. Blokkerend voor K4 en L2 | rapport oud vs. nieuw aantal chunks; index < 7 dagen oud |
| **WP-10** | 3 | Module K4 volledig, inclusief de vaste sectie "wat hier misging" en conserven | drie testbezoekers ronden af zonder hulp |
| **WP-11** | 3 | Modules K1 en K5 (nul modelbeurten) | route van drie modules voelt af |
| **WP-12** | 5 | `ops/runbook.md`: budget bijstellen, module publiceren, uitwijken naar conserven, herstel na crash, meldingen afhandelen | tweede persoon lost een storing op |

**Begin met WP-01, WP-02 en de inspectiehelft van WP-09.** Die drie samen bepalen hoeveel het atelier
aankan, welk model het beste past, en of de chatbot inhoudelijk sterk genoeg is om als lesmateriaal te
dienen. Alles daarna hangt van die uitkomsten af.

### Repostructuur

```
leeratelier/
  README.md  LICENSE
  config/     budget.yaml  modellen.yaml
  spec/       00-visie.md 01-competenties.md 02-toegang-en-budget.md
              03-architectuur.md 04-besluitenlog.md 05-open-vragen.md
  content/    modules/k00…k08/  modules/w01…w04/  modules/l01…l03/
              conserven/  beheerkaart-sjabloon.md
  app/        main.py render.py schema.py budget_ui.py melding.py   # :8793
  gateway/    main.py wachtrij.py budget.py cache.py conserven.py logboek.py   # :8794
  ops/        systemd/ ijking/ ijkset-nl.jsonl runbook.md
```

Stack identiek aan de rest: FastAPI, server-rendered HTML, stdlib waar het kan, geen frontend-framework.

---

## 11. Risico's

| Risico | Kans | Effect | Beheersing |
|---|---|---|---|
| **MoE werkt niet op deze chip** | reëel | beste modelkeuze valt weg | WP-02 vroeg; dense 8B als terugvaloptie |
| **Permanent open + beheerder afwezig** | zeker | storing blijft dagen staan | onbewaakt bedrijf §4.2 + eerlijke verwachting op de inlogpagina |
| **RAG-index te dun** | hoog | de chatbot ondermijnt je eigen betoog | WP-09 blokkerend voor K4 en L2 |
| **Beheerkaarten verdampen** | hoog | tweede helft van de visie sneuvelt | maandelijkse tegenspraaksessie §7 |
| **Bus factor 1** | zeker | atelier stopt bij afwezigheid | WP-12; "iedereen met login" betekent *gebruiken*, niet *beheren* |
| **Modules blijven concept** | middel | route voelt half af | `status`-veld + K1/K5 kosten nul beurten |
| **Logging als privacyprobleem** | middel | vertrouwen weg | doel en 90 dagen expliciet op de inlogpagina |
| **W1 wordt voor echt aangezien** | middel | verkeerde verwachting over een emulatie | waarschuwing ín de module, niet in een voetnoot |

---

## 12. Waar dit plan het kwetsbaarst is

1. **"Iedereen met login" beantwoordt de verkeerde vraag.** Gebruiken kan iedereen; *beheren* kan alleen jij.
   Bij permanent bedrijf is dat een groter risico dan bij dagvensters, want een storing om 22:00 blijft
   staan tot je wakker bent. Óf een tweede persoon met sudo en Tailscale, óf de verwachting expliciet
   verlagen. Niet allebei overslaan.
2. **Zelfbediening levert kennis, geen initiatieven.** De maandelijkse sessie is niet een extraatje maar de
   enige schakel tussen route en praktijk.
3. **Het budget in §4.4 is gerekend, niet gemeten.** Behandel het als hypothese tot WP-01 klaar is.
4. **Het modeladvies is gebaseerd op openbare bronnen van augustus/september 2026, niet op eigen tests op
   jouw machine.** De ijkset (WP-03) is er om dat advies te vervangen door metingen. Doe dat voordat je
   iets definitief kiest.
