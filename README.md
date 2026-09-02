# Leeratelier

**Een leerlaag over de POC's op orin3: verschillende doelgroepen laten leren met wat er al draait.**

> ⚠️ **Experimenteel — persoonlijk micro-innovatielab.** In dezelfde lijn als WaterLab en
> LeefomgevingLab: indicatief, geen operationeel systeem, geen opleidingsinstituut.

Het atelier bouwt geen nieuwe POC's. Het ontsluit de twaalf bestaande projecten langs zes leerlijnen,
voor doelgroepen die uiteenlopen van architecten tot ambtenaren met een dilemma.

## Status

**Fase 0 — infrastructuur staat, spec volgt.** De spec wordt buiten dit project opgesteld
(Claude desktop) en landt in `spec/`.

## Waar begin je

| Bestand | Wat |
|---|---|
| `docs/inventaris-orin3.md` | Geverifieerde inventaris: 12 projecten, 50+ publieke routes, volledige technische configuratie, 6 leerlijnen, 15 openstaande spec-vragen |
| `spec/` | De spec zodra die er is |
| `CLAUDE.md` | Werkinstructies + valkuilen |
| `~/sysmonitor/BACKLOG.md` | Technische randvoorwaarden die leerlijnen blokkeren |

## Structuur

```text
spec/       de spec + genomen besluiten
docs/       inventaris, uitwerkingen, achtergrond
materiaal/  lesmateriaal per leerlijn
```

## Nog te regelen

- **GitHub-remote** bestaat nog niet. Aanmaken kan pas als `gh` weer geldig ingelogd is
  (`gh auth login -h github.com`, scopes `repo` + `read:org`), daarna:
  `gh repo create bopfelix-derwisch/leeratelier --private --source=. --remote=origin`
  en `git remote set-url origin git@github.com:bopfelix-derwisch/leeratelier.git` (SSH-conventie).
- **Licentie** — nog geen keuze gemaakt; zie `~/sysmonitor/BACKLOG.md` A1. Dit is de eerste repo
  waar het meteen goed kan.
