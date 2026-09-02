# Conserven

Voorberekende antwoorden per module. Twee functies:

1. **Piek afvlakken.** In een atelier stelt iedereen ongeveer dezelfde vragen. De demovragen worden vooraf
   berekend; de tweede tot en met twaalfde bezoeker krijgen ze gratis.
2. **Uitwijk bij storing.** Het atelier is permanent open en onbewaakt. Conserven maken de hele route
   beschikbaar terwijl er geen model draait. Dat is geen noodrem maar een volwaardig pad.

Formaat per module, `k04.json`:

```json
{
  "module_id": "k04-wanneer-klopt-het-niet",
  "gegenereerd_op": "2026-…",
  "model": "…",
  "antwoorden": [
    { "vraag_genormaliseerd": "…", "antwoord": "…", "bron_labels": ["…"] }
  ]
}
```

Een conserf-antwoord wordt in het portaal **altijd zichtbaar gelabeld** als voorberekend. Een atelier dat
leert antwoorden te wantrouwen, mag zelf niet verzwijgen waar een antwoord vandaan komt.

Gegenereerd door WP-05, gevoed door `ops/ijkset-nl.jsonl`. Niet in git (zie `.gitignore`).
