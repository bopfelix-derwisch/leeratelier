# Modulecontract

Elke module is een map onder `content/modules/<id>/` met minstens `module.md`. Optioneel:
`opdracht.md` (het bewijsstuk) en `begeleiding.md` (alleen facilitator, nooit tonen).

`content/modules/k04-wanneer-klopt-het-niet/` is het referentievoorbeeld. Volg dat.

## Frontmatter

```yaml
id: k04-wanneer-klopt-het-niet   # gelijk aan de mapnaam
titel: "Wanneer klopt het antwoord niet?"
spoor: basis                     # basis | waterlab | leefomgeving
volgorde: 40                     # sorteervolgorde binnen het spoor
competenties: [B2, B3]           # uit 01-competenties.md
duur_min: 35
beurten: 3                       # modelbeurten; wordt vooraf gereserveerd
modellen: [klas, show]           # leeg = kost niets
conserven: conserven/k04.json    # null als de module geen model gebruikt
status: concept                  # concept | gepubliceerd
wat_ging_mis: true               # verplichte sectie aanwezig
bewijs: "…"                      # wat de bezoeker oplevert
poc: leefomgevinglab             # welke POC wordt gebruikt
routes: ["/chatbot", "/api/chat"]
```

## Regels

1. **`beurten` is niet decoratief.** Het portaal reserveert dit aantal vóórdat de bezoeker begint, zodat
   niemand halverwege zonder budget valt. Klopt het niet met de praktijk, pas dan de frontmatter aan —
   niet het budget.
2. **`wat_ging_mis: true` verplicht de sectie "Wat hier misging".** Ontbreekt die, dan faalt het renderen
   met een duidelijke fout. Dit is met opzet streng: fouten uit dit lab zijn het waardevolste materiaal
   dat er is, en ze moeten niet stilletjes wegvallen als iemand haastig een module schrijft.
3. **Modules met `beurten: 0` zijn goud.** Ze kosten niets en dragen evenveel bij. K1 en K5 zijn zulke
   modules; bouw ze vroeg zodat de route snel af aanvoelt.
4. **`status: concept` is zichtbaar voor de facilitator, niet voor bezoekers.** Zo kun je incrementeel
   publiceren zonder een halve route te tonen.
5. **Elke module eindigt met een doorverwijzing** naar wat logisch volgt.

## Vaste opbouw van module.md

1. Aanleiding — waarom deze module bestaat, in de taal van de doelgroep
2. Wat je nodig hebt en wat het kost aan beurten
3. Wat je gaat zien — een tabel die de kern samenvat
4. De proeven, elk met: wat je doet · wat je ziet · wat er onder de motorkap gebeurt · het signaal in je
   eigen werk · wat je checkt
5. **Wat hier misging** — echte fouten uit dit lab, geen verzonnen voorbeelden
6. Wat je meeneemt — de rij voor de beheerkaart
7. Doorverwijzing

De vier vaste haakjes per proef (**wat er gebeurt · het signaal · wat je checkt**) zijn wat de module
bruikbaar maakt voor functioneel beheerders. Zonder die drie is het een demonstratie.
