# Overdracht — 5 september 2026

Geschreven aan het eind van een lange sessie, voor de volgende sessie of een tweede persoon.
Feitenbron blijft `CLAUDE.md` (machine), `docs/inventaris-orin3.md` (projecten) en
`spec/05-besluitenlog.md` (afwijkingen). Dit bestand is het startpunt, geen kopie daarvan.

## Waar het staat

Het atelier draait en is publiek bereikbaar achter Cloudflare Access.

| | |
|---|---|
| Portaal | https://leeratelier.felixisfelix.com · lokaal `:8793` · `atelier-portaal.service` |
| Bemiddelaar | lokaal `:8794` · `atelier-bemiddelaar.service` · niet publiek |
| Klasmodel | `:8081` · `llama-klasmodel.service` · Qwen3-8B Q4_K_M, 4 slots x 4096 |
| Statuspagina | https://status.felixisfelix.com · `:8795` · geen inlog (besluit B28) |
| Toegang | Cloudflare Access, alleen het adres van de eigenaar |

Alle vier de diensten stonden bij het schrijven op `active`.

**Twee routes**, met een keuzemenu op `/start` (besluit B34):

| route | sporen | modules | duur | beurten | eindproduct |
|---|---|---|---:|---:|---|
| Beheer en techniek | basis, waterlab, leefomgeving | 16 | 470 min | 7 | `/beheerkaart` |
| Sturing | sturing (S0-S6) | 7 | 160 min | 2 | `/besluitkaart` |

Drieëntwintig gepubliceerde modules (basis 9, sturing 7, waterlab 4, leefomgeving 3) plus een
proefmodule op `concept`. Alle modules spreken de bezoeker met **je** aan, ook de sturingsroute.

## Wat deze sessie is veranderd

Drie dingen, alle drie gecommit op `master`.

1. **`df6e273` landingspagina als verhaal.** Zeven acten in chronologische volgorde met per act
   een eigen SVG-visual, en de rijpheid zichtbaar per project zodat af en onaf niet door elkaar
   lopen. Carrousel draait op een timer, niet op een animatielus.
2. **`86a0b6b` module K7 "De sleutelbos" + labs-mcp als dertiende project.** `~/labs-mcp` stond
   niet in de inventaris. De module behandelt wat een MCP-server is, de eerste stap (2 van de 12
   aangesloten), de latere fase, en het open-source-dilemma. De oude beheerkaart is K8 geworden.
   Alle tellingen van twaalf naar dertien.
3. **`ffc2151` latencywaarschuwing gerepareerd.** Zie besluitenlog V35. Was op drie manieren fout.

## Wat een volgende sessie moet weten

**`~/sysmonitor` staat niet onder versiebeheer.** De bijbehorende helft van reparatie 3 zit
daar (`check_leeratelier` en `advise`) en is dus niet gecommit. Back-up van de vorige versie:
`/home/bob/sysmonitor/sysmonitor.py.bak-2026-09-05`. Wil je die reparatie behouden, zet
`sysmonitor` onder git; dat staat al als los eind in K1 en de backlog.

**De GitHub-remote is er sinds 5 september 2026:**
`git@github.com:bopfelix-derwisch/leeratelier.git`, privé, branch **`main`**. De lokale branch
heette `master` en is meegehernoemd. Pushen gaat over SSH zonder token; de `gh`-CLI is nog
steeds niet ingelogd, maar die is alleen voor API-werk nodig.

**Twee sleutels moeten worden vervangen.** De Cloudflare-tunneltoken is tijdens deze sessie in
een gesprek geplakt en moet daarom als gelekt gelden. En `Derwisch_local/.env` bevat vier levende
sleutels; daar is een `.gitignore` op gezet, maar vervangen is nog niet gebeurd. Dit is precies
het onderwerp van K7 en het eerste werk van WP-21.

**Raak `:8080` niet aan.** Dat showmodel is van Derwisch. Nooit herstarten vanuit dit project.

**Twee modellen van ~19 GB passen niet naast elkaar.** Zie besluitenlog V4.

## Openstaand

### Beslissingen van de eigenaar
- **Open vraag 1** — naam voor de copyrightregel in `NOTICE`. Niet af te leiden, dus niet gegokt.
- **Open vraag 2** — bus factor 1. Bij permanent onbewaakt bedrijf het grootste risico.
- **Open vraag 4** — starten op dagbudget 300 of eerst een maand op 150.
- **Studio-PIN** staat in de git-geschiedenis van een ander project. Bewust niet gerepareerd:
  vraagt een herstart en een force-push, en dat is jouw keuze.

### Werk
- **WP-21** de overige tien projecten op de kluis aansluiten. Raakt draaiende POC's en vraagt
  herstarts — niet zelfstandig doen.
- **WP-00, WP-10, WP-18** staan op `[~]`: grotendeels af, met resten in de backlog beschreven.
- **K4-testronde** met drie functioneel beheerders. Dat is de poort uit het plan (B2/B3).
- **Eerste tegenspraaksessie** inplannen; `begeleide_sessie.datum` in `config/budget.yaml` staat
  nog op `null`.
- **Reboottest** van `llama-klasmodel` bij de eerstvolgende geplande herstart.

## Verificatie na een wijziging

```bash
cd /mnt/nvme/workspaces/leeratelier
python3 ops/valideer.py            # modulecontract + verwijzingen: "alles consistent"
python3 -m pytest tests/ -q        # 55 groen
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -m json.tool
```

Storingen: `ops/runbook.md`, veertien situaties. Situatie 4 gaat over de latency en zegt nu
expliciet dat je eerst naar `p95_traagste_model` kijkt voordat je een gelijktijdigheid verlaagt.

## Push

De repo staat op GitHub en lokaal en remote wijzen naar dezelfde commit.

```bash
git push                                          # branch main, over SSH
```

De eerste push moest de "Initial commit" van het aanmaakscherm opnemen: die had een eigen README
en geen gemeenschappelijke voorouder. Opgelost met een merge (`--allow-unrelated-histories`,
README-conflict in ons voordeel beslecht) in plaats van een force-push, zodat er niets is
weggegooid. De SSH-conventie van deze machine is hard — **nooit een token in een remote-URL.**
