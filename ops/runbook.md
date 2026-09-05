# Runbook — leeratelier

Doel: **iemand die dit niet gebouwd heeft, lost er een storing mee op.**

Het atelier staat permanent en onbewaakt open. De beheerder is niet altijd bereikbaar. Alles hieronder is
op 3 september 2026 uitgevoerd en werkt; commando's die niet getoetst zijn, staan er niet in.

> Werk vanaf `/mnt/nvme/workspaces/leeratelier`. Passwordless sudo staat aan.

---

## 0. Eerst dit: waar kijk je

```bash
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -m json.tool
systemctl status atelier-portaal atelier-bemiddelaar llama-klasmodel --no-pager
free -m | head -2 && df -h / /mnt/nvme | tail -2
```

De eerste regel vertelt bijna alles. Zo ziet gezond eruit:

```json
{"klasmodel": "actief", "showmodel": "actief", "embeddings": "actief",
 "wachtrij_diepte": 0, "dagbudget_verbruikt_pct": 4,
 "rag_index_leeftijd_dagen": 0, "storingsmodus": false, "open_meldingen": 0}
```

Antwoordt `:8794` helemaal niet, ga dan naar **situatie 2**.

### De vier diensten en waar ze voor zijn

| dienst | poort | valt hij weg, dan |
|---|---|---|
| `atelier-portaal` | 8793 | ziet de bezoeker niets meer |
| `atelier-bemiddelaar` | 8794 | blijven de pagina's werken, maar vragen stellen kan niet |
| `llama-klasmodel` | 8081 | gaan vragen naar het showmodel: trager, en gedeeld met Derwisch |
| `leefomgevinglab-embed` | 8082 | werkt de zoekindex niet meer (niet van dit atelier, wel nodig) |

Het **showmodel** op 8080 is van Derwisch. **Herstart dat niet om een atelier-probleem op te lossen.**

---

## 1. Klasmodel weg

**Wat de bezoeker ziet:** een gele banner dat vragen naar het showmodel gaan. Antwoorden komen gewoon,
maar trager en gelabeld als `showmodel`.

**Hoe erg:** niet erg. Dit mag een nacht wachten.

```bash
systemctl is-active llama-klasmodel
sudo systemctl restart llama-klasmodel
journalctl -u llama-klasmodel -n 50 --no-pager        # als het niet lukt
```

Laden duurt ongeveer een minuut. Controleren:

```bash
curl -s http://127.0.0.1:8081/v1/models | head -c 120
```

**Komt hij niet omhoog wegens geheugen** (`cudaMalloc failed: out of memory` in het journaal):

```bash
free -m | head -2                                     # kijk naar buff/cache
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
sudo systemctl restart llama-klasmodel
```

Het geheugen is *unified*: NvMap kan page-cache niet zelf opeisen, dus 20 GB "available" betekent niet
20 GB bruikbaar. `drop_caches` is veilig en raakt geen enkele draaiende dienst.

---

## 2. Bemiddelaar weg

**Wat de bezoeker ziet:** een rode banner, "de leerbemiddelaar is niet bereikbaar". Pagina's werken,
vragen stellen niet.

```bash
sudo systemctl restart atelier-bemiddelaar
until curl -sf http://127.0.0.1:8794/health; do sleep 1; done
```

**Blijft hij omvallen**, kijk dan naar het journaal. De twee oorzaken die voorkomen:

```bash
journalctl -u atelier-bemiddelaar -n 50 --no-pager
```

- *fout in `config/budget.yaml` of `config/modellen.yaml`* — de dienst leest die bij het starten. Toets ze
  met `python3 -c "import yaml; yaml.safe_load(open('config/budget.yaml'))"`.
- *database niet schrijfbaar* — `ls -l /mnt/nvme/leeratelier/atelier.db`, moet van `bob` zijn.

---

## 3. Portaal weg

```bash
sudo systemctl restart atelier-portaal
until curl -sf http://127.0.0.1:8793/health; do sleep 1; done
curl -s http://127.0.0.1:8793/gezondheid | python3 -m json.tool
```

`modules_stuk` groter dan nul betekent dat een module niet aan het contract voldoet; het veld `fouten`
zegt welke en waarom. Het portaal blijft dan gewoon staan — alleen die ene module ontbreekt.

**Portaal draait maar is van buiten onbereikbaar:** dan ligt het aan de tunnel of aan Tailscale, niet aan
de dienst. Zie situatie 8.

---

## 4. Wachtrij loopt vol

**Wat de bezoeker ziet:** langere wachttijden; boven een rijdiepte van 8 krijgt hij meteen een conserf.
Dat is ontworpen gedrag, geen storing.

```bash
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -c \
  'import json,sys; d=json.load(sys.stdin); print("rij:", d["wachtrij_diepte"], "p95:", d["p95_latency_ms"], \
   "ms over", d["p95_metingen"], "metingen; traagste model:", d["p95_traagste_model"])'
```

**Staat de p95 op 0?** Dan zijn er minder dan tien geslaagde antwoorden in de afgelopen 24 uur en doet de
bemiddelaar met opzet geen uitspraak — bij zo weinig metingen is de p95 gewoon het maximum. Dat is geen
storing en de statuspagina meldt het dan ook als OK. Zie besluitenlog V35.

**Kijk naar `p95_traagste_model` voordat je iets verlaagt.** `leefomgevinglab` betekent de POC-route via
`:8792`, en die is met opzet de trage weg omdat de ophaalstap erin zit — daar helpt geen enkele instelling
van het atelier aan. Alleen bij `show` of `klas` is de gelijktijdigheid hieronder de juiste knop.

Blijft de rij diep, kijk dan eerst of het klasmodel draait (situatie 1). Vrijwel altijd is dat de oorzaak:
alles staat dan in de rij voor het trage showmodel.

Helpt dat niet, verlaag dan de gelijktijdigheid van het showmodel in `config/budget.yaml`:

```yaml
gelijktijdig:
  showmodel: 1        # was 2
```

En herstart de bemiddelaar. **Verhoog nooit** het aantal om een wachtrij op te lossen; de machine zit bij
één gebruiker al op 93 procent GPU en meer gelijktijdigheid koopt alleen wachttijd.

---

## 5. Handmatig uitwijken naar conserven

Wanneer je dit doet: er is iets mis met de modellen dat je niet meteen kunt oplossen, en je wilt dat het
atelier blijft werken met voorberekende antwoorden.

```bash
cp config/budget.yaml config/budget.yaml.bak
sed -i 's/^dagbudget_modelbeurten: .*/dagbudget_modelbeurten: 0/' config/budget.yaml
sudo systemctl restart atelier-bemiddelaar
```

Vanaf dat moment krijgt elke vraag het conserf van die module, gratis en zichtbaar gelabeld als
voorberekend. Alleen modules zónder conserf geven een nette weigering.

Terugzetten:

```bash
cp config/budget.yaml.bak config/budget.yaml
sudo systemctl restart atelier-bemiddelaar
curl -s http://127.0.0.1:8794/v1/budget/x | python3 -m json.tool     # dag_totaal terug op 300
```

**Welke modules hebben een conserf?**

```bash
ls content/conserven/*.json
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -c \
  'import json,sys; print(json.load(sys.stdin)["conserven"], "conserven geladen")'
```

Nieuwe conserven maken uit een ijkset-run:

```bash
python3 ops/maak-conserven.py --ijkset ops/ijking/ijkset-qwen3-8b-2026-09-02.jsonl \
  --module k04-wanneer-klopt-het-niet --domeinen vergunningen geluid meta
sudo systemctl restart atelier-bemiddelaar
```

---

## 6. Dagbudget te snel op

Kijk **eerst** of het klasmodel draait. Een weggevallen klasmodel stuurt alles naar het trage showmodel,
en dan lijkt het budget hard te lopen terwijl het probleem ergens anders zit.

```bash
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -c \
  'import json,sys; d=json.load(sys.stdin); print(d["klasmodel"], d["dagbudget_verbruikt_pct"], "%")'
```

Pas als het klasmodel draait en het budget echt op is, is verhogen een optie. Een veilige stap is 300 naar
450 — dat is nog altijd ruim onder wat de machine aankan (gemeten: het klasmodel haalt 20 antwoorden per
minuut bij twee gelijktijdige bezoekers).

```bash
sed -i 's/^dagbudget_modelbeurten: .*/dagbudget_modelbeurten: 450/' config/budget.yaml
sudo systemctl restart atelier-bemiddelaar
```

Noteer de wijziging in `spec/05-besluitenlog.md`. Het budget is een besluit, geen instelling.

---

## 7. Zoekindex verouderd

De gezondheidsendpoint meldt `rag_index_leeftijd_dagen`. Boven de 30 dagen is dat een waarschuwing, boven
de 90 een alarm.

```bash
python3 ops/ijking/rag_inspect.py --dir /mnt/nvme/geluidsmeter/data/rag
```

Herbouwen duurt ongeveer drie minuten:

```bash
cp -r /mnt/nvme/geluidsmeter/data/rag /mnt/nvme/geluidsmeter/data/rag-backup-$(date +%F)
cd /mnt/nvme/workspaces/LeefomgevingLab && python3 scripts/07_build_rag_index.py
```

**Niet tijdens openingstijd.** Twee bezoekers die dezelfde vraag stellen krijgen tijdens een herbouw
verschillende antwoorden, en modules K4 en spoor L worden er onvoorspelbaar van.

Terugzetten als het misgaat:

```bash
cp /mnt/nvme/geluidsmeter/data/rag-backup-<datum>/* /mnt/nvme/geluidsmeter/data/rag/
```

---

## 8. Module publiceren of terugzetten

Een module staat in `content/modules/<id>/module.md`. In de frontmatter bovenaan staat `status`.

```bash
sed -i 's/^status: gepubliceerd/status: concept/' content/modules/w03-casussen/module.md
sudo systemctl restart atelier-portaal
```

Concept betekent: onzichtbaar voor bezoekers, wel zichtbaar op `/facilitator`. Publiceren gaat andersom.

**Controleer altijd na een wijziging** of de module nog rendert:

```bash
python3 ops/valideer.py
curl -s http://127.0.0.1:8793/gezondheid | python3 -c \
  'import json,sys; d=json.load(sys.stdin); print("stuk:", d["modules_stuk"], d["fouten"])'
```

Een gepubliceerde module met `wat_ging_mis: true` **moet** een sectie "Wat hier misging" hebben, anders
weigert hij te renderen. Dat is met opzet.

---

## 9. Meldingen uit de "ik kom er niet uit"-knop

```bash
python3 - <<'EOF'
import sqlite3, json
con = sqlite3.connect("/mnt/nvme/leeratelier/atelier.db"); con.row_factory = sqlite3.Row
for r in con.execute("SELECT id, tijdstip, bezoeker_id, module_id, tekst, context "
                     "FROM meldingen WHERE afgehandeld=0 ORDER BY id"):
    print(f"#{r['id']} {r['tijdstip'][:16]} {r['bezoeker_id']} [{r['module_id']}]")
    print(f"   {r['tekst']}")
    print(f"   context: {json.dumps(json.loads(r['context']), ensure_ascii=False)}")
EOF
```

De context bevat de laatste vraag, waar dat antwoord vandaan kwam, de budgetstand, de status van beide
modellen en de leeftijd van de index. Dat is meestal genoeg om te zien wat er gebeurde zonder terug te
hoeven vragen.

Afhandelen:

```bash
python3 -c "import sqlite3; c=sqlite3.connect('/mnt/nvme/leeratelier/atelier.db'); \
  c.execute('UPDATE meldingen SET afgehandeld=1 WHERE id=?',(1,)); c.commit()"
```

---

## 10. Herstel na een reboot

Alle vier de units zijn `enabled` en starten mee. In deze volgorde komen ze op:

```bash
systemctl is-enabled llama-klasmodel atelier-bemiddelaar atelier-portaal
systemctl is-active  llama-klasmodel atelier-bemiddelaar atelier-portaal
```

Het klasmodel heeft ongeveer een minuut nodig. De bemiddelaar en het portaal starten in seconden en
verdragen het als het model er nog niet is: de bemiddelaar valt terug op conserven, en zodra het model
er is werkt alles vanzelf weer.

> **Nog niet waargenomen.** Dat dit zo werkt is afgeleid uit `is-enabled` en de unit-bestanden, niet uit
> een echte herstart. Bij de eerstvolgende geplande reboot: controleer het en haal deze regel weg.

---

## 11. Een nieuwe publieke hostname toevoegen

**Bescherming eerst, route erna.** Maak altijd de Access-applicatie en de policy aan vóórdat het
DNS-record bestaat. Andersom staat de dienst een tijd onbeschermd op het internet, en als de tweede stap
mislukt blijft dat zo.

1. Access-applicatie plus policy aanmaken (Zero Trust → Access → Applications).
2. CNAME naar `ca12e4f6-fa0d-4f39-8868-e729d9369c5c.cfargotunnel.com`, **proxied aan**.
3. Ingress-regel toevoegen aan de tunnel. Dat is een `PUT` die de héle lijst vervangt: lees eerst de
   bestaande configuratie uit en voeg toe, anders verdwijnen de andere hostnames.

```bash
# huidige ingress uitlezen voordat je iets vervangt
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/67284ed7b6c2adc4704afa1fdc1fbc4b/cfd_tunnel/ca12e4f6-fa0d-4f39-8868-e729d9369c5c/configurations"
```

Controleer daarna dat een onbeveiligd bezoek op de Access-inlog uitkomt en dat er geen inhoud lekt.

## 12. Het portaal bekijken via Tailscale

Zolang Cloudflare Access er niet staat, is het portaal alleen binnen het tailnet te bekijken. De dienst
zelf blijft op `127.0.0.1`; Tailscale zet er een proxy voor.

```bash
sudo tailscale serve --bg --https=443 http://127.0.0.1:8793   # aanzetten
tailscale serve status                                        # controleren
sudo tailscale serve --https=443 off                          # uitzetten
```

Bereikbaar op **https://orin3.tail897ef4.ts.net/**.

**Dit is geen toegangsbeveiliging.** Binnen het tailnet is er geen inlog: iedereen deelt hetzelfde budget
en dezelfde naam, en wie een `Cf-Access-Authenticated-User-Email`-header meestuurt, is die persoon. Het
portaal zegt dat zelf in een banner. Zet dit uit zodra Access er staat, of eerder als er iemand anders in
het tailnet komt.

---

## 13. Wat je nooit doet

- **Een POC-repo aanraken** om een atelier-probleem op te lossen.
- **Het showmodel op 8080 herstarten.** Dat is van Derwisch. Het atelier kan zonder; Derwisch niet.
- **De RAG-index herbouwen tijdens openingstijd.** Zie situatie 7.
- **Het dagbudget verhogen om een klacht op te lossen.** Kijk eerst of het klasmodel draait.
- **De gelijktijdigheid verhogen om een wachtrij op te lossen.** Dat maakt het trager, niet sneller.

---

## 14. Wanneer bel je de beheerder

Bijna nooit. Dit atelier is ontworpen om zonder ingrijpen te blijven werken: alle units herstarten
zichzelf, een weggevallen model wordt opgevangen, en conserven houden de route overeind als er niets
meer draait.

Bel wel bij:

- **de schijf boven de 90 procent** — `df -h /`. Dat legt uiteindelijk de hele machine plat, en dat is
  geen atelier-probleem meer.
- **een POC die eruit ligt** en die je niet met een herstart terugkrijgt.
- **meldingen die inhoudelijk zijn** in plaats van technisch. Die gaan over lesmateriaal, en daar gaat
  deze runbook niet over.

Voor de rest geldt wat op de inlogpagina staat: dit is een privé-lab van één persoon, en storingen kunnen
dagen duren. Dat is geen zwaktebod maar een afspraak.

---

## 15. Een bezoeker heeft zich gemeld

De "ik kom er niet uit"-knop schrijft naar de tabel `meldingen`. Openstaande meldingen zie je zo:

```bash
python3 - <<'EOF'
import sqlite3
con = sqlite3.connect("file:/mnt/nvme/leeratelier/atelier.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
for r in con.execute("SELECT id, tijdstip, module_id, tekst FROM meldingen "
                     "WHERE afgehandeld IS NULL OR afgehandeld=0 ORDER BY id"):
    print(f"#{r['id']} {r['tijdstip'][:16]} {r['module_id']}: {r['tekst']}")
EOF
```

**Laat er een voorstel bij maken:**

```bash
cd /mnt/nvme/workspaces/leeratelier
python3 ops/meldingen-verwerken.py              # voorstellen, niets wordt gewijzigd
python3 ops/meldingen-verwerken.py --groot      # zelfde, met het 32B-showmodel
```

Het verslag komt in `ops/meldingen/verwerkt-<datum>.md`.

**Lees het voorstel altijd voordat je het doorvoert.** De vier grendels (regelaanwijzing binnen
de module, contract, `valideer.py`, git-commit) vangen verzonnen wijzigingen af, maar niet slechte
redactie: bij een lezersvraag over een link stelde het model voor die link te verwijderen. Zie V38.

**Doorvoeren, als het voorstel deugt:**

```bash
python3 ops/meldingen-verwerken.py --toepassen --melding 7
sudo systemctl restart atelier-portaal
```

Elke wijziging is een aparte commit. Terugdraaien is `git revert <commit>`.

**Liever laten voorleggen dan zelf zoeken?** Er staat een Claude Code-agent klaar in
`.claude/agents/meldingen.md`. Die haalt de open meldingen op, leest de module erbij, controleert of
de klacht klopt (inclusief het echt opvragen van genoemde links) en legt per melding een voorstel
voor. Hij wijzigt niets. Starten met `/agents` of door erom te vragen; agentdefinities worden bij
sessiestart ingelezen, dus na het aanmaken van een nieuwe agent eerst een nieuwe sessie.

Wil je dat dagelijks, dan zijn er twee manieren:

| manier | duurzaam? |
|---|---|
| Een cron in de lopende Claude-sessie | nee: verdwijnt met de sessie en vervalt na zeven dagen |
| Een systemd-timer die `claude -p` aanroept | ja, ook na een herstart |

De tweede staat er nog niet; de units in `ops/systemd/atelier-meldingen.*` draaien het script,
niet de agent.

**Melding afvinken** als je hem met de hand hebt opgelost:

```bash
python3 -c "import sqlite3; c=sqlite3.connect('/mnt/nvme/leeratelier/atelier.db'); \
c.execute('UPDATE meldingen SET afgehandeld=1 WHERE id=?', (7,)); c.commit()"
```
