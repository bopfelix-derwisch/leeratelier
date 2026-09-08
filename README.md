# Leeratelier

> **Experimenteel — persoonlijk micro-innovatielab.** In dezelfde lijn als Waterlab en
> LeefomgevingLab: indicatief, geen operationeel systeem, geen opleidingsinstituut. Die disclaimer
> moet meeschalen zodra er werkelijk lesgegeven wordt.

Een dunne laag naast dertien bestaande POC's op `orin3`. Bezoekers loggen in, lopen een route van modules
door, stellen vragen aan lokale taalmodellen, en gaan weg met een **beheerkaart** voor hun eigen toepassing.

**Twee doelgroepen, twee routes** (besluit B34, 5 september 2026). De route **Beheer en techniek** is
voor functioneel beheerders, product owners en technisch geïnteresseerden; de route **Sturing** is voor
informatiemanagers, programmamanagers en algemeen managers, en eindigt in een *besluitkaart* in
plaats van een beheerkaart. Het keuzemenu staat op `/start`.

**Doelgroep van de basisroute:** functioneel beheerders en technisch geïnteresseerden. Zij bouwen niets. Zij gebruiken de
POC's om te begrijpen wat er onder de motorkap gebeurt en wanneer een AI-antwoord niet deugt.

**Visie:** het vak van informatieprofessional opnieuw vormgeven met AI, en met dat leerproces concrete
initiatieven op gang brengen. Met nieuwe instrumenten leren spelen in hetzelfde orkest.

## Beginnen

1. `CLAUDE.md` — werkinstructies, de machinewerkelijkheid en de valkuilen van deze hardware
2. `spec/plan-v0.3.md` — het volledige plan; leidend bij twijfel
3. `spec/06-backlog.md` — werkpakketten in volgorde, met verificatiecommando's

De eerste drie taken zijn WP-01 (ijkmeting), WP-02 (MoE-verificatie) en de inspectiehelft van WP-09.
Die bepalen hoeveel het atelier aankan, welk model past, en of de chatbot inhoudelijk sterk genoeg is
om lesmateriaal te zijn. **Bouw geen portaal voordat die metingen er liggen.**

## Draaien

```bash
python3 ops/ijking/rag_inspect.py --dir /mnt/nvme/geluidsmeter/data/rag
python3 ops/ijking/meet.py --endpoint http://127.0.0.1:8080 --concurrency 1 2 4 --n 6
bash    ops/ijking/moe_check.sh /mnt/nvme/nvme/models/<moe-model>.gguf
```

## Structuur

```
CLAUDE.md              werkinstructies voor Claude Code
config/                budget.yaml, modellen.yaml
spec/                  plan, competenties, modulecontract, besluitenlog, backlog
content/modules/       de modules; k04 is het referentievoorbeeld
content/conserven/     voorberekende antwoorden, ook de uitwijk bij storing
app/                   portaal :8793
gateway/               leerbemiddelaar :8794
ops/                   ijking, systemd-units, ijkset, runbook
docs/                  inventaris-orin3.md: de geverifieerde feitenbron over de machine
```

De oude map `materiaal/` is vervallen: lesmateriaal staat vanaf nu in `content/modules/`.

## Status

**Fase 0 — fundament.** Het startpakket (spec, contracten, ijkgereedschap) staat; er is nog niets
gebouwd. De eerste drie taken zijn WP-01, WP-02 en de inspectiehelft van WP-09; zie `spec/06-backlog.md`.

## Nog te regelen

- ~~**GitHub-remote** bestaat nog niet.~~ **Geregeld 5 september 2026:**
  `git@github.com:bopfelix-derwisch/leeratelier.git`, privé, branch **`main`** (was lokaal `master`).
  Pushen gaat over SSH en vraagt geen token. De `gh`-CLI is nog steeds niet ingelogd; dat is alleen
  nodig voor API-werk, niet om te pushen.
- **Licentie** — vastgesteld op **Apache-2.0** (besluit B18, 3 september 2026) en toegepast in alle tien
  de repo's op deze machine. De canonieke tekst staat ongewijzigd in `LICENSE`; de appendix is niet
  ingevuld, dus er is nog geen `NOTICE` met een rechthebbende. Zie open vraag 1.

## Verwante documenten buiten deze repo

| Bestand | Wat |
|---|---|
| `docs/inventaris-orin3.md` | geverifieerde inventaris van dertien projecten en de volledige configuratie van orin3 |
| `~/sysmonitor/BACKLOG.md` | technische randvoorwaarden die leerlijnen blokkeren (secties A en B) |
| `~/.claude/CLAUDE.md`, `/home/bob/ORIN3_SYSTEEM.md` | machine-brede context en infra-documentatie |
