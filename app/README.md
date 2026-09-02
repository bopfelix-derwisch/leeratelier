# Atelier-portaal :8793 — contract

Bouwopdracht: WP-06. Bindt op `127.0.0.1:8793`. Publiek via Cloudflare Access op
`leeratelier.felixisfelix.com`.

FastAPI met Jinja2 en server-rendered HTML. Geen frontend-framework. Eén klein inline script is
toegestaan: het pollen van `/v1/taak/{id}`.

## Routes

| Route | Doet |
|---|---|
| `GET /` | overzicht van de route: modules per spoor, status per module, budgetmeter |
| `GET /module/{id}` | gerenderde module uit `content/modules/{id}/module.md` |
| `POST /module/{id}/vraag` | proxy naar de bemiddelaar; geeft een taak-id terug |
| `GET /taak/{taak_id}` | proxy voor het pollen |
| `GET /opdracht/{id}` | de opdracht bij een module |
| `GET /beheerkaart` | invulformulier op basis van `content/beheerkaart-sjabloon.md` |
| `POST /beheerkaart/export` | levert de ingevulde kaart als markdown-download |
| `POST /vastgelopen` | melding met contextvangst naar de bemiddelaar |
| `GET /gezondheid` | voor sysmonitor |

## Vaste elementen op elke pagina

- **budgetmeter**: "nog 9 van 15 beurten vandaag". Zichtbaar, niet weggestopt.
- **bronlabel** bij elk antwoord: uit cache, klasmodel, showmodel of conserf. Een bezoeker die leert
  antwoorden te wantrouwen, moet kunnen zien waar dit antwoord vandaan komt.
- **storingsbanner**, gezet vanuit `/v1/gezondheid`. Permanent open en onbewaakt betekent dat een storing
  zichzelf moet aankondigen.
- **"ik kom er niet uit"-knop**. Toont eerst zelfhulp en de conserven, verstuurt dan pas een melding, en
  noemt een realistische reactietermijn.

## Renderen van modules

Frontmatter volgens `spec/04-modulecontract.md`. Regels:

- `status: concept` verschijnt niet in de route van gewone bezoekers.
- `beurten` wordt vooraf gereserveerd via `POST /v1/reserveer` bij het openen van de module.
- `wat_ging_mis: true` betekent dat de sectie "Wat hier misging" verplicht aanwezig moet zijn; ontbreekt
  die, dan faalt het renderen met een duidelijke fout in plaats van stil door te gaan.
- `begeleiding.md` wordt **nooit** aan bezoekers getoond.

## Toon

Nederlands, zakelijk, geen uitroeptekens, geen emoji. De bezoeker is een vakvolwassen beheerder, geen
cursist.
