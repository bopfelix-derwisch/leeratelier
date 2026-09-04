---
id: l03-het-antwoordcontract
titel: "Het antwoordcontract — en waarom te streng ook fout is"
spoor: leefomgeving
volgorde: 30
competenties: [B2, B6]
duur_min: 30
beurten: 2
modellen: [klas]
conserven: conserven/l03-het-antwoordcontract.json
status: gepubliceerd
wat_ging_mis: true
bewijs: "het antwoordcontract van je eigen toepassing, met eigenaar"
poc: leefomgevinglab
routes: ["/api/chat"]
---

# Het antwoordcontract

Om elk antwoord van deze chatbot zit een schil: een disclaimer, een verwijzing naar het bevoegd gezag, en
een vlag die zegt of het systeem zeker is. Samen heet dat het antwoordcontract.

Het is de meest onderschatte laag van een AI-toepassing. Hij bepaalt niet wát het systeem zegt, maar
**hoe stellig** — en daarmee wat een gebruiker ermee doet.

**Wat het kost:** 2 modelbeurten.

---

## Wat het contract bevat

Elk antwoord van deze POC krijgt vier velden mee:

| veld | wat erin staat |
|---|---|
| `antwoord` | de tekst van het model |
| `disclaimer` | "indicatief, geen juridisch besluit" |
| `vangnet` | verwijzing naar het bevoegd gezag of het Omgevingsloket |
| `onzekerheid` | een vlag die zegt of het systeem twijfelt |

Drie van die vier zijn vaste teksten. De vierde is een vaste waarde.

---

## Proef 1 · De vlag die altijd op waar staat

Stel een vraag waarvan het antwoord letterlijk in de bron staat. Stel daarna een vraag die daar zeker
buiten valt.

**Kijk naar:** het veld `onzekerheid` in beide antwoorden. Het vraagblok onderaan deze pagina toont het
onder elk antwoord, samen met de disclaimer en het vangnet — precies zoals de chatbot ze meegeeft.

**Wat er onder de motorkap gebeurt.** In de broncode van deze POC staat het veld op vier plaatsen, en
overal zo:

```python
{"vraag": activiteit, "bron": BRON, "onzekerheid": True,
 "disclaimer": DISCLAIMER, "vangnet": VANGNET}
```

**`onzekerheid` wordt nergens berekend.** Het staat altijd op waar. Een antwoord dat woordelijk uit een
opgehaald fragment komt, draagt dezelfde vlag als een antwoord dat het model volledig zelf verzon.

Dat is geen slordigheid maar een echt probleem: een systeem dat zijn eigen zekerheid wil melden, moet
weten wanneer het iets niet weet. Dat is precies wat een taalmodel niet kan.

**Signaal in je eigen werk:** een betrouwbaarheidsscore die altijd hetzelfde is, of altijd hoog. Vraag hoe
hij berekend wordt. "Dat komt uit het model" is geen antwoord — vraag door uit welk getal.

**Wat je checkt:** varieert de zekerheidsindicatie over verschillende vragen? Zo niet, dan is het geen
indicatie maar decoratie.

---

## Proef 2 · Te streng is ook fout

Formuleer een vraag waarvan je zeker weet dat het antwoord in de documentatie staat, maar vraag om een
oordeel: niet *"wat staat er over X"* maar *"mag ik X"*.

**Kijk naar:** krijg je de informatie die er wél is, of vooral een verwijzing?

**Wat er onder de motorkap gebeurt.** Het vangnet is er met goede reden: dit systeem mag geen juridische
uitspraken doen. Maar een contract dat te ver doorslaat, onderdrukt informatie die het systeem gewoon
gevonden had. De gebruiker krijgt dan een correcte, veilige, nutteloze zin.

Dat is de spanning van deze module, en er bestaat geen instelling die hem oplost. Te losjes en het systeem
beweert dingen die het niet mag beweren; te streng en niemand gebruikt het meer.

**Signaal in je eigen werk:** gebruikers die zeggen *"hij zegt nooit iets nuttigs"* melden zelden een kapot
systeem. Ze melden meestal een te streng contract — en dat is instelbaar, mits iemand doorheeft dat dat de
oorzaak is.

**Wat je checkt:** wie mag het contract wijzigen, en waar staat het? Als het antwoord "ergens in een prompt"
is, beheert niemand het.

---

## Proef 3 · Een bronvermelding is ook maar tekst

Vraag om een antwoord met bronvermelding en probeer één genoemde bron te openen.

**Wat hier op 3 september 2026 gebeurde.** Gevraagd wat `Lden` betekent, antwoordde de chatbot dat het
staat voor *"Lärmpegel Dauer nacht"* — een uitschrijving die niet bestaat. En eronder stonden vier
IPLO-bronnen als onderbouwing, waaronder
`iplo.nl/thema/geluid/geluid-regelgeving/geluidproductieplafond/`.

In geen van die vier pagina's komt het woord `Lden` voor.

**Wat er onder de motorkap gebeurt.** Het ophaalmechanisme leverde de dichtstbijzijnde stukken over geluid
in het algemeen. Het model schreef uit eigen geheugen. De bronnenlijst werd erbij gezet omdat er stukken
opgehaald wáren — niet omdat het antwoord eruit kwam.

En het contract werkte gewoon: `onzekerheid: true`, disclaimer, verwijzing naar het bevoegd gezag. Al die
schillen zaten er keurig omheen, om een verzonnen antwoord met vier links eronder.

**Een bronvermelding bewijst niet dat het antwoord uit die bron komt.**

**Signaal in je eigen werk:** verwijzingen die je niet in twee klikken kunt narekenen. En breder: een
contract dat altijd hetzelfde zegt, geeft geen informatie over dít antwoord.

**Wat je checkt:** is er een koppeling tussen het opgehaalde fragment en de zin in het antwoord, of staan
de bronnen er als lijst onder? Dat verschil is groot en het is zelden zichtbaar.

---

## Wat hier misging

*(Deze sectie staat in elke module. Het zijn echte fouten uit dit lab, niet verzonnen voorbeelden.)*

- **Er is geen vastgelegde afweging over het contract.** In een eerdere versie van deze module stond dat de
  ontwerpers zelf hadden opgeschreven dat het contract nuttige informatie niet mag onderdrukken. Bij het
  natrekken bleek dat nergens te staan. De claim is geschrapt en vervangen door wat wél te controleren is:
  de vaste `True`. Dat een module over het wantrouwen van bronnen zelf een onverifieerbare bron aanhaalde,
  is de scherpste fout van deze route.
- **Het contract is verspreid over vier plaatsen.** Vier bestanden zetten dezelfde velden op dezelfde
  waarden. Wie de disclaimer wil wijzigen, moet ze alle vier vinden.
- **Het contract werkte precies zoals bedoeld op een fout antwoord.** Bij het Lden-voorbeeld hierboven
  gingen alle waarschuwingen af, en dat hielp niets. Waarschuwingen die altijd afgaan, dragen geen
  informatie.

---

## Wat je hiervan meeneemt

Het bewijsstuk: **het antwoordcontract van jouw toepassing**, met eigenaar.

| vraag | jouw antwoord |
|---|---|
| Welke schillen zitten er om een antwoord heen? | |
| Welke daarvan zijn vaste tekst, welke worden berekend? | |
| Wie mag ze wijzigen, en staat dat in versiebeheer? | |
| Wanneer is het contract voor het laatst gewijzigd, en waarom? | |
| Krijgen gebruikers wel eens een correct maar nutteloos antwoord? | |

De laatste vraag stel je aan gebruikers, niet aan de leverancier.

**Volgende:** spoor W, over het Waterlab — en over een nagebouwd vakinterface dat er precies uitziet als
de echte dienst.
