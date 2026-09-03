# Backlog — werkpakketten in volgorde

Eén werkpakket tegelijk, van boven naar beneden. Elk pakket heeft een **klaar-als** en een
**verificatie**. Vink af met `[x]` en noteer afwijkingen in `05-besluitenlog.md`.

Legenda: 🔴 blokkerend voor alles daarna · 🟡 blokkerend voor een specifieke module · ⚪ vrij inplanbaar

---

## Fase 0 · Fundament

### [~] WP-00 🔴 Fundament op orde
**Grotendeels afgerond 2026-09-03.** Vier van de zes deeltaken zijn klaar; twee liggen bij de eigenaar
omdat ze het Cloudflare-dashboard of een draaiende dienst raken.
**Doel:** alles wat een bezoeker straks ziet, is juridisch en technisch vertoonbaar.

Deeltaken, elk apart af te vinken:
- [x] **Licentiebesluit — Apache-2.0** (besluit B18). Canonieke tekst, sha256 `cfc7749b…`, 202 regels,
      ongewijzigd in **alle tien** de repo's, elk in een eigen commit die uitsluitend `LICENSE` bevat
      zodat de vuile werkbomen onaangeroerd bleven.
- [x] **`docuchat`, `transcribe`, `sysmonitor` in git.** Geheimencheck vóór de eerste commit, daarna
      `.gitignore`, daarna committen. Buiten git gehouden: `sysmonitor/.auth` (gebruiker + sha256 van het
      wachtwoord), `history.jsonl` en `public/status.json` (gegenereerd), een `.bak`-bestand, en
      `docuchat/.env` — met een `.env.example` ernaast voor de sleutelnamen.
- [ ] **TLS-fout oplossen.** `admin.helper.felixisfelix.com` valt buiten Cloudflare Universal SSL (vierde
      niveau). Voeg in het Zero Trust-dashboard `helper-admin.felixisfelix.com` toe naar `localhost:8788`
      en werk verwijzingen bij. **Ligt bij de eigenaar: dit is een dashboard-actie, niet vanaf de machine
      te doen.** Gemeten 2026-09-03: beide hostnames geven geen verbinding, dus de nieuwe bestaat nog niet.
- [x] **API-titel corrigeren.** `Geluidsmeter API` → `LeefomgevingLab API` in
      `src/leefomgevinglab/geluidsmeter/api.py` regel 85. Gecommit. **Werkt pas na een herstart van de
      dienst**; niet herstart, want de POC is publiek bereikbaar.
- [x] **Apex onderzocht.** Gemeten: `felixisfelix.com` geeft 200 en wordt door Vercel geserveerd
      (`x-vercel-cache: HIT`). Op `:8790` draait de Derwisch-transcriptiepagina, geen tweede apex-site.
      Vanaf deze machine is geen dubbele belegging waarneembaar; of er in het Zero Trust-dashboard nog een
      Public Hostname op de apex staat, is alleen daar te zien. Zie vondst V12.
- [x] **Geheimencheck uitgevoerd — en die leverde de belangrijkste vondst van dit werkpakket op.**
      `Derwisch_local` had **geen `.gitignore`** en een ongenegeerde `.env` met `OPENAI_API_KEY`,
      `GITHUB_TOKEN`, `CF_TOKEN_FELIXISFELIX` en `VERCEL_TOKEN`, in een repo met 39 gewijzigde bestanden en
      een GitHub-remote. Opgelost (V10). `morele-helper`, `LeefomgevingLab` en `waterlab` negeerden hun
      `.env` al correct.
- [ ] **Studio-PIN uit de historie halen — ligt bij de eigenaar.** De PIN staat als hardcoded fallback in
      `Derwisch_local/server.mjs` regel 65 en als waarde in `HANDOVER_Derwisch_local_1700.md`, in twee
      commits. Roteren vraagt een herstart van `derwisch_local-backend.service`; uit de historie halen
      vraagt een herschreven geschiedenis en een force-push. Zie vondst V11.

**Klaar als:** elke repo heeft een licentiebestand, de drie losse projecten zitten in git, en
`helper-admin.felixisfelix.com` geeft een 401 in plaats van een TLS-fout.

**Stand 2026-09-03:** de eerste twee zijn gehaald (10/10 repo's met licentie, 3/3 projecten in git). De
derde wacht op een dashboard-actie. Fase 0 is daarmee niet volledig af, maar wel zover als vanaf de
machine mogelijk is.

**Verificatie:**
```bash
for r in ~/morele-helper ~/Derwisch_local ~/sysmonitor ~/docuchat ~/transcribe \
         ~/BluesLab ~/felix-nazaten /mnt/nvme/workspaces/LeefomgevingLab /mnt/nvme/workspaces/waterlab; do
  printf '%-50s ' "$r"; git -C "$r" ls-files | grep -qi '^LICENSE' && echo OK || echo ONTBREEKT
done
curl -sI https://helper-admin.felixisfelix.com | head -1
curl -s http://127.0.0.1:8792/openapi.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["info"]["title"])'
```

---

## Fase 1 · IJking, ijkset en modelkeuze

### [x] WP-01 🔴 IJkmeting: wat kan deze machine werkelijk aan
**Doel:** het dagbudget uit §4.4 van het plan vervangen door gemeten getallen.
**Afgerond 2026-09-02** — rapport: `ops/ijking/rapport-2026-09-02.md`.

`ops/ijking/meet.py` staat er al. Draai hem tegen het showmodel bij oplopende gelijktijdigheid, meet
p50/p95, tokens per seconde, tijd tot eerste token, en geheugen vóór en na.

- [x] meting bij 1, 2, 4 en 8 gelijktijdige verzoeken — 32/32 geslaagd, nul fouten
- [x] geheugenmeting met `free -m` en `tegrastats` rond elke run — `Tegrastats` toegevoegd aan `meet.py`
- [x] rapport naar `ops/ijking/rapport-<datum>.md`
- [x] `config/budget.yaml` bijstellen op basis van de uitkomst — 300 beurten/dag, 20 per bezoeker,
      `gelijktijdig.showmodel` 1 → 2

**Uitkomst in één regel:** de GPU staat op 93-96% bij élk gelijktijdigheidsniveau, dus de machine is al
bij één gebruiker verzadigd; gelijktijdigheid koopt doorzet met wachttijd. De knik ligt bij 2.
Drie vondsten die de documentatie tegenspreken staan in `spec/05-besluitenlog.md` (V1-V3); **V1 raakt
WP-04 direct**.

**Klaar als:** er staat een reproduceerbaar rapport met p50/p95 per gelijktijdigheidsniveau, en
`config/budget.yaml` bevat getallen die uit dat rapport volgen in plaats van uit een schatting.

**Verificatie:**
```bash
python3 ops/ijking/meet.py --endpoint http://127.0.0.1:8080 --concurrency 1 2 4 --n 6 \
  --out ops/ijking/rapport-$(date +%F).json
```

### [x] WP-02 🔴 MoE-verificatie op SM87
**Afgerond 2026-09-02** — rapport: `ops/ijking/moe-verificatie-2026-09-02.md`. Antwoord: **MoE werkt**,
en is 5,4x sneller dan het dense showmodel. Besluit B16 in `05-besluitenlog.md`; vondsten V4 en V5.
**Doel:** vaststellen of Mixture-of-Experts-modellen op deze chip en deze build werken. Dit bepaalt of
Gemma 4 26B-A4B (3,8B actief van 25,2B, dus 4B-snelheid bij veel hogere kwaliteit) een optie is — op
papier het beste dat deze machine kan draaien.

Achtergrond: `ggml-org/llama.cpp` issue #19219 meldt dat MoE-decode hangt op Jetson Orin AGX (SM87) voor
alle builds ná b7309 (dec 2025). Deze machine draait build 8117. De melding is van januari 2026 en kan
inmiddels opgelost zijn.

- [x] check of het issue inmiddels gesloten is en of er een fix in een latere build zit — gesloten als
      `not_planned`/`stale`, dus **niet** opgelost verklaard; de oorzaak
      (`CUDA_SCALE_LAUNCH_QUEUES`, commit `a83c73a18`) is wel gereverteerd in PR #19227 en is met
      `strings` aantoonbaar afwezig in build 8117
- [x] download één MoE-GGUF naar `/mnt/nvme/nvme/models/` (**niet naar `/`**) —
      `qwen3-30b-a3b/Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf`, 18,4 GB; `/` bleef op 82%
- [x] draai `ops/ijking/moe_check.sh` — GESLAAGD, antwoord in 1 s
- [x] bij hangen: n.v.t. — het hangt niet. In plaats daarvan gemeten hoe snel het is (35,1 tegen
      6,5 tok/s) en het besluit dense-versus-MoE onderbouwd: **variant A**, MoE vervangt het showmodel

**Klaar als:** in `05-besluitenlog.md` staat een schriftelijk ja/nee met bewijs (output of timeout), en
een besluit over dense versus MoE.

**Uitvoering van variant A is bewust níet gedaan** — het showmodel vervangen raakt een draaiende dienst
(Derwisch) en is een keuze van de eigenaar, geen uitkomst van de meting. Werk voor WP-03/WP-04.

**Verificatie:**
```bash
bash ops/ijking/moe_check.sh /mnt/nvme/nvme/models/<moe-model>.gguf
```

### [x] WP-03 🔴 Nederlandse ijkset
**Afgerond 2026-09-02** — rapport: `ops/ijking/ijkset-rapport-2026-09-02.md`.
**Klasmodel wordt `Qwen3-8B` Q4_K_M** (besluit B17).
**Doel:** een vaste set van twintig Nederlandse domeinvragen waarmee elk kandidaat-model beoordeeld wordt.
Dit is tegelijk de selectieprocedure, de conserven-voorraad en het complete lesmateriaal van module K3.

`ops/ijkset-nl.jsonl` staat er al met twintig vragen. Bouw het script dat elk model erlangs haalt.

- [x] `ops/ijking/ijkloop.py`: stond er al en werkt ongewijzigd
- [x] minstens drie modellen doorlopen — het zijn er **vijf** geworden, de vijf klassen uit plan §5.4:
      32B dens, 30B MoE, 12B dens, 8B dens, 4B dens. **100/100 antwoorden geslaagd**
- [x] een vergelijkingstabel genereren (model × vraag × tijd × oordeel) — `ops/ijking/beoordeel.py`
      toegevoegd, want `ijkloop.py --vergelijk` geeft alleen tijd en lengte, en daarmee wint een model
      dat snel drie regels produceert
- [x] de vraag "welk model wordt klasmodel" beantwoorden en vastleggen — **Qwen3-8B**, besluit B17;
      `config/modellen.yaml` en `ops/systemd/llama-klasmodel.service` zijn ingevuld

**Klaar als:** er ligt een matrix van minstens 3 modellen × 20 vragen, en het klasmodel is gekozen met
motivatie in `05-besluitenlog.md`.

**Doorslaggevend was ijk-20**, de vraag naar de eigen herkomst: Qwen3-8B is het enige van de vijf dat
trainingsdata en peildatum noemt. Het 4B-model verzint daar instanties die niet bestaan.
**Vondst V6:** op ijk-12 (asvolgorde) faalt élk model — het beste lesmateriaal dat de set opleverde.
**Vondst V7:** Qwen3-8B heeft `--reasoning-budget 0` nodig; die vlag staat nu in de unit voor WP-04.

### [x] WP-04 🔴 Klasmodel permanent op :8081
**Doel:** een snel, meertalig dens model dat permanent draait naast het showmodel.
**Afgerond 2026-09-03** — rapport: `ops/ijking/klasmodel-2026-09-03.md`. Draait: `Qwen3-8B` Q4_K_M.

Let op: `--ctx-size` is het **totaal** zodra `--parallel` expliciet staat. Bij `--parallel 4` dus
`--ctx-size 16384` voor 4096 per slot. **Getoetst bij dit werkpakket** — de correctie die WP-01 op deze
regel aanbracht (vondst V1) was fout en is teruggedraaid.

- [x] geheugenmeting vóór de start: 35 894 MB in gebruik
- [x] systemd-unit op basis van `ops/systemd/llama-klasmodel.service`, geïnstalleerd en enabled
- [x] `Restart=always` en `StartLimitIntervalSec=0`, want het atelier draait permanent en onbewaakt
- [x] geheugenmeting ná de start: proces `VmRSS` 7,58 GB; met alle drie de modellen draaiend staat de
      machine op ~36 van 62,8 GB, dus **ruim 25 GB over** — genoeg voor variant A uit besluit B16
- [x] gelijktijdigheid gemeten (stond nog als gok in `config/budget.yaml`): 10,9 / 20,5 / 24,4 / 25,4
      antwoorden per minuut bij 1 / 2 / 4 / 8. `gelijktijdig.klasmodel: 4` blijkt juist
- [x] geverifieerd dat `--reasoning-budget 0` werkt: geen `<think>`-blok in het antwoord (V7)

**Klaar als:** de unit is enabled en active, overleeft een reboot, en `/v1/models` antwoordt op :8081.

> **Nog niet afgevinkt: de reboot.** Een herstart van `orin3` legt Derwisch, LeefomgevingLab, waterlab,
> de relays en sysmonitor tegelijk plat; dat is geen beslissing van een werkpakket. `is-enabled` geeft
> `enabled` en het symlink in `multi-user.target.wants/` staat er, dus de unit hoort mee te starten —
> maar dat is een redenering, geen waarneming. **Toets dit bij de eerstvolgende geplande herstart.**

**Verificatie:**
```bash
systemctl is-enabled llama-klasmodel && systemctl is-active llama-klasmodel
curl -s http://127.0.0.1:8081/v1/models | head -c 200; echo
free -m | head -2
```

### [x] WP-09a 🔴 RAG-index inspecteren
**Afgerond 2026-09-03** — rapport: `ops/ijking/rag-inspectie-2026-09-03.md`.
**Doel:** vaststellen hoe klein de index werkelijk is. `vectors.npy` is 33 KB; bij bge-m3 (1024 dim) is
dat ongeveer 8 chunks fp32. Als dat klopt, beantwoordt de vergunningen-chatbot vragen uit een handvol
fragmenten van juni — te dun voor lesgebruik, maar wél uitstekend materiaal voor module K4.

`ops/ijking/rag_inspect.py` staat er al.

- [x] vorm, dtype en aantal vectoren uitlezen — `(8, 1024)`, `<f4`
- [x] aantal chunks en totale tekstlengte in `chunks.jsonl` — 8 fragmenten, 8.187 tekens
- [x] bouwdatum en welke bronnen erin zitten — 21 juni, **twee** IPLO-pagina's
- [x] bevindingen naar `ops/ijking/rag-inspectie-<datum>.md`

**Klaar als:** het exacte aantal chunks bekend is en vastligt.

**Verificatie:**
```bash
python3 ops/ijking/rag_inspect.py --dir /mnt/nvme/geluidsmeter/data/rag
```

---

## Fase 2 · Wandelend skelet

Doel van deze fase: een **dunne maar complete keten** van inlog tot antwoord. Alles aanwezig, niets diep.
Niet verder gaan voordat een testbezoeker end-to-end door een dummy-module heen komt.

### [x] WP-05 🔴 Leerbemiddelaar :8794
Zie `gateway/README.md` voor het volledige API-contract en de datamodellen.
**Afgerond 2026-09-03** — rapport: `ops/ijking/bemiddelaar-2026-09-03.md`. 21 tests.

- [x] HTTP-API zoals gespecificeerd — alle zes de endpoints, plus `/health` voor systemd
- [x] wachtrij met positiefeedback binnen 2 s — **gemeten: acht verzoeken in 0,25 s**
- [x] dag- en persoonsbudget uit `config/budget.yaml`, met automatische reset om middernacht
      — de reset is een gevolg van de sleutel `(bezoeker, datum)`, geen taak die kan missen
- [x] cache op `sha256(genormaliseerde vraag + module_id + model)`
- [x] conserven-terugval uit `content/conserven/` — vijf echte conserven voor K4,
      gegenereerd uit de ijkset-antwoorden van Qwen3-8B (WP-03)
- [x] degradatieladder: cache → klasmodel → showmodel → conserf → licht pad
- [x] logboek in sqlite met 90 dagen bewaartermijn en een opruimtaak (elke zes uur,
      niet op een kloktijd: een taak die op middernacht wacht mist zijn slag bij herstart)
- [x] bindt op `127.0.0.1:8794` — geverifieerd met `ss -ltn`

**Klaar als:** 8 gelijktijdige verzoeken krijgen allemaal binnen 2 s een status, niemand valt stil, het
budget wordt correct afgeboekt, en bij een gestopt model valt alles netjes terug op conserven.

**Gemeten tegen het echte klasmodel:** acht verzoeken ingediend in 0,25 s, alle acht beantwoord na 9 s,
budget exact acht afgeboekt (292 van 300 over). Met `systemctl stop llama-klasmodel` valt een vraag
automatisch terug op het showmodel, zichtbaar gelabeld als `bron: show`.

> **Trede 4 is met tests getoetst, niet live.** Conserven komen pas in beeld als *beide* modellen weg
> zijn, en het showmodel op :8080 is dat van Derwisch. Dat stilleggen om een eigen werkpakket af te
> vinken is niet in verhouding. Twee tests dekken het: conserf zonder beurtkosten, en een nette uitleg
> als er ook geen conserf is.

**Verificatie:**
```bash
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -m json.tool
systemctl stop llama-klasmodel && curl -s -X POST http://127.0.0.1:8794/v1/vraag \
  -H 'content-type: application/json' \
  -d '{"module_id":"k04-wanneer-klopt-het-niet","vraag":"test","bezoeker_id":"test"}' | python3 -m json.tool
systemctl start llama-klasmodel
```

### [x] WP-06 🔴 Atelier-portaal :8793
Zie `app/README.md` voor routes en schermen.
**Afgerond 2026-09-03** — rapport: `ops/ijking/portaal-2026-09-03.md`. 16 tests, 39 in totaal.

- [x] routerenderer op het modulecontract uit `04-modulecontract.md` — `app/schema.py` dwingt het af;
      regel 2 (`wat_ging_mis` verplicht de sectie) laat een gepubliceerde module hard falen
- [x] budgetmeter zichtbaar op elke pagina — in de balk, "nog 19 van 20 beurten vandaag"
- [x] "ik kom er niet uit"-knop met contextvangst — module, laatste vraag, bron van dat antwoord,
      budgetstand, status van beide modellen, leeftijd van de index, storingsmodus
- [x] storingsbanner in vier gradaties, gevoed door `/v1/gezondheid` van de bemiddelaar
- [x] bindt op `127.0.0.1:8793` — geverifieerd met `ss -ltn`
- [x] één dummy-module om de keten te bewijzen — `content/modules/k00-proefmodule/`

**Klaar als:** een testbezoeker logt in, doorloopt de dummy-module, verbruikt budget, krijgt bij uitputting
een conserf, en dat is terug te vinden in het logboek.

**Live doorlopen** met een Access-header: route (concept onzichtbaar) → module openen (20 → 19) →
vraag (`bron=klas`, `model=Qwen3-8B`, index 0 dagen) → dezelfde vraag (`bron=cache`, 0 beurten) →
terug te vinden in het logboek. De uitputting-naar-conserf is met een test gedekt: dat leegmaken kost
twintig modelaanroepen en de test doet het in een fractie van de tijd.

> **Dit portaal mag nog niet publiek.** `bezoeker_van()` leest de Access-header maar valt terug op een
> vaste naam als die ontbreekt; zonder Access ervoor kan iedereen elke identiteit claimen door een header
> mee te sturen. Blijft op `127.0.0.1` tot WP-07 staat. Waarschuwing staat ook op `/facilitator`.

### [ ] WP-07 🔴 Toegang en privacy
- [ ] Cloudflare Access met e-mail-OTP op `leeratelier.felixisfelix.com` → `127.0.0.1:8793`
- [ ] bemiddelaar :8794 is **niet** publiek bereikbaar, alleen via het portaal
- [ ] bezoeker-identiteit uit de Access-header koppelen aan het persoonlijke budget
- [ ] privacytekst op de inlogpagina: wat er gelogd wordt, waarom, en 90 dagen bewaartermijn
- [ ] eerlijke verwachtingstekst: *dit is een privé-lab van één persoon; storingen kunnen dagen duren*

### [x] WP-08 🟡 Sysmonitor-uitbreiding
**Afgerond 2026-09-03.** Sectie "Leeratelier" in `~/sysmonitor/sysmonitor.py`, gevoed door
`/v1/gezondheid` van de bemiddelaar. De drie nieuwe units (`llama-klasmodel`,
`atelier-bemiddelaar`, `atelier-portaal`) staan nu ook in `SERVICES`.
Zes nieuwe drempels, in het bestaande patroon: elke warn/crit krijgt een concrete actie via `advise()`.

| Signaal | warn | crit | Actie |
|---|---|---|---|
| Dagbudget verbruikt | 70% | 90% | standaard naar klasmodel |
| Wachtrijdiepte | 4 | 8 | terugvallen op conserven |
| p95 antwoordlatency | 60 s | 120 s | showmodel uit de route |
| Leeftijd RAG-index | 30 d | 90 d | herbouwen |
| Klasmodel niet actief | — | direct | unit :8081 herstarten |
| Openstaande meldingen | 3 | 10 | mail naar beheerder |

- [x] drempels toegevoegd, met `advise()`-teksten in het Nederlands — elk met een
      uitvoerbaar commando, niet met "onderzoek dit nader"
- [x] de storingsbanner van het portaal wordt hierdoor gezet — sysmonitor schrijft
      `/mnt/nvme/leeratelier/storing.json`, het portaal leest dat en toont de banner

**Live getoetst:** met `llama-klasmodel` gestopt gaat sysmonitor naar `crit`, schrijft de banner,
en ziet een bezoeker op `/` de tekst *"Er is een storing: klasmodel. Waar een voorberekend antwoord
klaarstaat krijg je dat, zichtbaar gelabeld."* Na herstarten is de banner binnen één sysmonitor-run
weer weg.

> Een banner ouder dan 90 minuten wordt genegeerd. Een sysmonitor die zelf stilvalt mag geen
> melding laten staan die niemand meer bijwerkt — dat is precies de storing die niemand opmerkt.

### [x] WP-09b 🟡 RAG-index herbouwen en vergroten
Blokkerend voor K4 en spoor L. Pas doen na WP-09a.
**Afgerond 2026-09-03** — besluit B19, vondsten V13 en V14.

- [x] `scripts/07_build_rag_index.py` opnieuw draaien met een ruimere bronset — **170 bronnen**,
      geselecteerd uit `iplo.nl/sitemap.xml` (8.585 pagina's) op de domeinen van de ijkset, elk vooraf
      geverifieerd op bereikbaarheid en tekstopbrengst
- [x] rapport oud versus nieuw aantal chunks — **8 → 924** (115x), 8.187 → 986.001 tekens (120x)
- [ ] index-leeftijd zichtbaar maken in de gezondheidsendpoint van de bemiddelaar — **kan pas bij WP-05**;
      die dienst bestaat nog niet. Het veld `rag_index_leeftijd_dagen` staat al in `gateway/README.md`

**Klaar als:** de index is jonger dan 7 dagen en het aantal chunks is met minstens een orde van grootte
gegroeid. **Gehaald:** 0 dagen oud, twee ordes van grootte gegroeid.

> **Het gat uit V8 is hiermee niet gedicht, en dat kan ook niet met IPLO.** `Lden`, `Lmax` en `dB(A)` komen
> in de index van 924 fragmenten nul keer voor, en geen enkele geluid-regelgevingspagina van IPLO noemt ze.
> IPLO gaat over de Omgevingswet, niet over akoestiek. Dat is een derde faalvorm naast de vier van K4: **de
> vraag valt buiten het bronbereik**. Gevraagd naar Lden verzint de chatbot "Lärmpegel Dauer nacht" en noemt
> daarbij vier IPLO-bronnen die het woord niet bevatten — het scherpste bewijsstuk dat dit project tot nu
> toe heeft opgeleverd. Zie vondst V13 en §4 van het rapport.

---

## Fase 3 · Eerste module volledig

### [~] WP-10 🔴 Module K4 "Wanneer klopt het niet"
De volledige inhoud staat al in `content/modules/k04-wanneer-klopt-het-niet/`.
**Inhoudelijk afgerond 2026-09-03; de testronde met mensen ligt bij de eigenaar.**

- [x] conserven genereren — 8 conserven uit de ijkset-run van Qwen3-8B, over vergunningen, geluid en meta,
      zodat alle proeven ook zonder model werken
- [x] de module laten renderen in het portaal — `status: gepubliceerd`, zichtbaar op de route
- [x] **de vaste sectie "wat hier misging" gecontroleerd tegen de POC's.** Drie van de vier bullets
      klopten niet meer of waren niet te verifiëren; zie hieronder
- [ ] **testronde met drie functioneel beheerders** — dit vraagt drie mensen. Niet iets wat vanaf de
      machine te doen is

**Klaar als:** drie testbezoekers ronden de module af zonder hulp en leveren het bewijsstuk van B2: drie
zelf gevonden foute antwoorden met diagnose.

**Wat de feitencontrole opleverde.** De sectie beweerde vier dingen; na toetsing tegen de POC's:

| claim | uitkomst |
|---|---|
| "De index staat stil sinds juni" | wás waar, 74 dagen — maar is op 3 september herbouwd. Herschreven naar de historische feiten mét de herbouw |
| "Een orde van grootte kleiner dan aangenomen" | waar, en nu meetbaar: 8 fragmenten uit twee pagina's, 8.187 tekens. Twee ordes eigenlijk |
| "De ontwerpers legden vast dat het contract niet mag onderdrukken" | **niet te verifiëren** — staat nergens. Vervangen door iets dat wél controleerbaar is: `onzekerheid` staat op vier plaatsen in de broncode als vaste `True` en wordt nergens berekend |
| "Gegokte endpoints klopten zelden" | waar, en letterlijk terug te vinden op de kwaliteitspagina van LeefomgevingLab, inclusief het concrete voorbeeld |

Er is een **vijfde faalvorm** bijgekomen die er niet stond: *buiten het bronbereik*. Die kwam boven bij
WP-09b en is de moeilijkste, omdat hij er precies uitziet als een te dunne index. En proef 4 heeft nu echt
bewijsmateriaal van deze machine: de chatbot verzon "Lärmpegel Dauer nacht" en noemde vier IPLO-bronnen
die het woord niet bevatten.

### [x] WP-11 ⚪ Modules K1 en K5

Beide kosten **nul modelbeurten** en geven je vrijwel gratis een route van drie modules die als geheel
aanvoelt. **Afgerond 2026-09-03.**

- [x] K1 Rondgang uitgeschreven — drie proeven op gemeten getallen van deze machine: 17 diensten,
      38 van 61 GB, 77 GB modellen, en het invulschema van zes onderdelen als bewijsstuk
- [x] K5 De bron veranderde uitgeschreven — vier proeven live tegen `/wfs-kwaliteit`, met echte cijfers
      uit de scan van 3 september: een laag met **94,3 procent ongeldige geometrieën**, vier IMEV-velden
      die de specificatie eist maar die niet in het schema zitten, en drie lagen die nul objecten bevatten
      terwijl ze netjes antwoorden
- [x] beide op `status: gepubliceerd`

De proefmodule uit WP-06 staat weer op `concept`: die bestond om de keten te bewijzen en is nu vervangen
door een echte route. Ze blijft voor de facilitator zichtbaar als snelle ketencontrole.

---

## Fase 4 · Incrementeel uitbreiden

In deze volgorde, steeds één module, steeds meteen live:

- [ ] **WP-12** K6 Draaiend houden (0 beurten)
- [ ] **WP-13** K7 Beheerkaart — invulformulier plus export naar markdown
- [ ] **WP-14** K3 Modellenbank — twee modellen live, drie uit conserven
- [ ] **WP-15** K2 De motorkap zonder mystiek
- [ ] **WP-16** Spoor L: L1 kwaliteit, L2 vergunningen-RAG van binnen, L3 antwoordcontract
- [ ] **WP-17** Spoor W: W1 FEWS-emulatie (mét de waarschuwing ín de module), W2 toen het misging,
      W3 casussen

---

## Fase 5 · Openstellen

### [ ] WP-18 🔴 Runbook
`ops/runbook.md` moet een tweede persoon in staat stellen een storing op te lossen.

- [ ] dag openen en sluiten, budget bijstellen
- [ ] een module publiceren of terugzetten naar concept
- [ ] handmatig uitwijken naar conserven
- [ ] herstel na crash van elk van de vier diensten
- [ ] meldingen uit de "vastgelopen"-knop afhandelen

**Klaar als:** iemand anders lost een gesimuleerde storing op zonder jou.

### [ ] WP-19 ⚪ Maandelijkse tegenspraaksessie inrichten
- [ ] reservering van 20% dagbudget op de sessiedag
- [ ] toelatingsvoorwaarde: basisroute afgerond plus beheerkaart meegebracht
- [ ] werkvorm vastleggen: geen les, maar zes mensen die elkaars beheerkaart aanvallen
