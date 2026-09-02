# Leeratelier — Claude Code instructies

> **Machine-breed:** `~/.claude/CLAUDE.md` + `ORIN3_SYSTEEM.md` — niet hier herhalen.
> **Domein:** Dwarsdoorsnede — een leerlaag óver alle POC's heen, geen eigen POC.
> **Start via** `orin3` → window **`0:leeratelier`** (pad `/mnt/nvme/workspaces/leeratelier`).

Leeratelier laat verschillende doelgroepen (meer) leren met behulp van de bestaande POC's op orin3.
Het bouwt zelf geen nieuwe POC's: het ontsluit wat er al draait, langs zes leerlijnen.

**Lees altijd eerst:** `docs/inventaris-orin3.md` — de geverifieerde inventaris van alle twaalf
projecten, de technische configuratie en de zes leerlijnen. Daarna `spec/` voor de actuele spec.

---

## ⚠️ Kritieke waarschuwingen

| # | Valkuil | Correct |
|---|---------|---------|
| 1 | `find ~` **bevriest** op orin3 | Gebruik `ls` of specifieke paden |
| 2 | Nieuwe mappen in `/mnt/nvme/workspaces/` vereisen **sudo** | De parent is van `marc`: `sudo mkdir … && sudo chown bob:bob …` |
| 3 | Dit project **raakt draaiende diensten** van andere labs | Nooit zomaar in `waterlab`/`LeefomgevingLab` ingrijpen — zie backlog-vraag 11 |
| 4 | De labs zijn **indicatief, geen operationeel systeem** | Die disclaimer moet meeschalen zodra er lesgegeven wordt |
| 5 | Repo heeft (nog) **geen licentie** | Zie `sysmonitor/BACKLOG.md` A1 — blokkeert de open-source-leerlijn |

---

## Structuur

```text
leeratelier/
  spec/       # de spec (komt vanuit Claude desktop) + besluiten
  docs/       # inventaris, uitwerkingen, achtergrond
  materiaal/  # lesmateriaal per leerlijn
```

---

## De zes leerlijnen

Uitgewerkt in `docs/inventaris-orin3.md` §3.

| # | Leerlijn | Primaire doelgroep | Leunt op |
|---|---|---|---|
| L1 | AI-architectuur | architecten, technisch leiders | hele lokale stack, relays, Waterlab FEWS/GraphQL |
| L2 | Datakwaliteit | data-eigenaren, stelselmensen | LeefomgevingLab `/kwaliteit` (al grotendeels geschreven) |
| L3 | Open source & open data beleid | beleid, CIO-office, juristen | alle repo's + de licentie-omissie zelf |
| L4 | Persoonlijk gebruik (how-to) | individuele professionals | Transcribe → Docuchat → BluesLab → Derwisch |
| L5 | Domeininhoud | waterbeheer, omgevingsdienst | Waterlab, LeefomgevingLab |
| L6 | Reflectie & oordeelsvorming | ambtenaren met dilemma's | Morele Helper, Derwisch |

---

## Afhankelijkheden buiten dit project

Dit project heeft geen eigen dienst en geen eigen poort. Het leunt op wat er draait:

- **Publieke demo's** — leefomgevinglab/waterlab/status/upload/felixisfelix.com via de cloudflared-tunnel
- **Lokale LLM** — Qwen2.5-32B op `:8080`, bge-m3 embeddings op `:8082`
- **Technische randvoorwaarden** — staan in **`~/sysmonitor/BACKLOG.md`** (secties A en B).
  A1 (licenties), A2 (RAG-index) en A3 (admin.helper TLS) blokkeren elk een leerlijn.

---

## Conventies

- Commits eindigen met de trailer uit `~/.claude/CLAUDE.md` (model dat de commit maakte).
- Alleen committen/pushen als erom gevraagd wordt.
- Remote is nog niet aangemaakt — zie `README.md`.
