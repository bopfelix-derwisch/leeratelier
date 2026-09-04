# De maandelijkse tegenspraaksessie

*Voor de facilitator. Niet zichtbaar voor bezoekers.*

Dit is de enige schakel tussen de route en de praktijk. Zonder deze sessie levert het atelier kennis op
en geen initiatieven, en dan sneuvelt de tweede helft van de visie. Zo staat het in het plan, en dat is
geen retoriek: een ingevulde beheerkaart wordt pas een besluit als iemand hem aanvalt.

---

## De vorm

| | |
|---|---|
| duur | twee uur |
| deelnemers | zes, niet meer |
| toelating | basisroute gedaan **en** je eigen beheerkaart meegebracht |
| capaciteit | 20 procent van het dagbudget is die dag voor deelnemers gereserveerd |
| wat het niet is | een les, een demo, een terugkoppeling op het atelier |
| wat het wel is | zes mensen die elkaars beheerkaart aanvallen, met de POC's binnen handbereik |

**Zes is een maximum, geen streefgetal.** Bij acht valt de sessie uiteen in twee gesprekken en kan niemand
meer alle kaarten volgen. Bij vier werkt het nog steeds.

---

## Waarom aanvallen, en niet bespreken

Een beheerkaart die niemand heeft tegengesproken, is een lijstje. De vraag is niet of iemand het er mee
eens is, maar of het standhoudt.

De drie vragen die een kaart moeten overleven:

1. **"Hoe weet je dat dit het eerst misgaat?"** — Bij vraag 1 van de kaart staan drie faalvormen. De
   meeste mensen schrijven de ergste op in plaats van de waarschijnlijkste. Vraag naar het voorbeeld.
2. **"Kun jij die check zelf uitvoeren?"** — Bij vraag 3 staat een handeling. Als die een ontwikkelaar
   vraagt, is het geen check maar een verzoek, en dan gebeurt hij niet.
3. **"Wat doe je als je leverancier nee zegt?"** — Bij vraag 5 staan drie vragen aan de leverancier. Een
   vraag zonder vervolgstap is een gesprek, geen instrument.

Dat zijn er drie omdat er in twee uur voor zes kaarten niet meer in past.

---

## Verloop

| tijd | wat |
|---|---|
| 0:00 | **Ronde langs de kaarten.** Elk twee minuten: welke toepassing, welke drie faalvormen. Niet meer. |
| 0:15 | **Twee kaarten uitkiezen** die het verst uiteenlopen. Niet de beste twee — de meest verschillende. |
| 0:20 | **Kaart één onder vuur.** Twintig minuten. De eigenaar antwoordt, de rest vraagt door. |
| 0:40 | **Kaart twee onder vuur.** Zelfde. |
| 1:00 | **Pauze.** |
| 1:10 | **Wat kwam er boven dat op meer kaarten thuishoort?** Dit is waar de opbrengst zit. |
| 1:35 | **Iedereen wijzigt zijn eigen kaart.** Stil, tien minuten, ter plekke. |
| 1:45 | **Eén afspraak per persoon**, hardop, met een datum. |
| 2:00 | Einde. |

De laatste twintig minuten zijn niet optioneel. Een sessie zonder gewijzigde kaarten en zonder afspraken
is een goed gesprek geweest, en daar is de sessie niet voor.

---

## Wat de facilitator vooraf doet

**Een week ervoor:**

- Zet de sessiedatum in `config/budget.yaml` en herstart de bemiddelaar:

  ```yaml
  begeleide_sessie:
    datum: "2026-10-01"
    deelnemers:
      - deelnemer1@voorbeeld.nl
      - deelnemer2@voorbeeld.nl
  ```
  ```bash
  sudo systemctl restart atelier-bemiddelaar
  ```

  Vanaf die dag krijgen gewone bezoekers 80 procent van het dagbudget; de rest blijft over voor de zes.
  Staat `datum` op `null`, dan verandert er niets.

- Controleer wie de route gedaan heeft:

  ```bash
  curl -s http://127.0.0.1:8794/v1/voortgang/deelnemer1@voorbeeld.nl | python3 -m json.tool
  ```

  Dat toont welke modules iemand geopend heeft. **Het zegt niets over de beheerkaart** — die brengt de
  deelnemer mee, en dat kan geen systeem vaststellen.

- Lees de openstaande meldingen (runbook, situatie 9). Wie is vastgelopen en waarop? Dat is gratis
  agenda-materiaal en het is actueler dan wat dan ook.

**De dag zelf:** controleer dat de keten draait (runbook, situatie 0). Een sessie waarin de chatbot niet
werkt, is geen ramp — de conserven vangen dat op — maar je wilt het weten voordat zes mensen zitten.

---

## Wat de facilitator níet doet

- **Geen presentatie.** Als je meer dan vijf minuten aan het woord bent, is het een les geworden.
- **Geen kaarten verbeteren.** Je stelt de derde vraag, je schrijft niet mee.
- **Geen verdediging van het atelier.** Kritiek op de modules is bruikbaar; die noteer je en je gaat
  verder. Het atelier is niet het onderwerp.
- **Geen consensus zoeken.** Twee mensen die het oneens blijven over een escalatiepunt hebben allebei iets
  geleerd. Eén afgedwongen conclusie leert niemand iets.

---

## Waar het misgaat

Dit is de eerste versie van deze werkvorm en er is nog geen sessie gehouden. Wat er op grond van het plan
te verwachten valt:

- **De kaarten zijn te abstract.** Mensen schrijven "het model kan fouten maken" in plaats van "de index
  is van juni en de regeling is in maart gewijzigd". Vraag bij elke faalvorm naar het laatste concrete
  voorval. Geen voorval betekent meestal geen faalvorm maar een zorg.
- **Iedereen is aardig.** Zes mensen uit hetzelfde vakgebied vallen elkaars werk niet spontaan aan. De
  drie vragen hierboven zijn er om dat te doorbreken zonder dat het persoonlijk wordt: ze gaan over de
  kaart, niet over de maker.
- **De afspraken verdampen.** Eén afspraak per persoon, hardop, met een datum, en de volgende sessie begin
  je ermee. Zonder dat is dit een leuke middag.
- **Er komt niemand.** Zes mensen die twee uur vrijmaken voor een privé-lab is niet vanzelfsprekend. Het
  plan noemt dit niet als risico; dat is een omissie. De uitnodiging moet komen van iemand die de
  deelnemers al kent.

---

## Waarop deze sessie wordt afgerekend

Uit het plan, fase 5: **zes bezoekers hebben een beheerkaart afgerond en drie daarvan hebben hem in het
eigen team besproken.** Op dit moment staat die teller op nul.

Dat is de maat, en het is een strengere maat dan bezoekersaantallen. Iemand die de hele route doorloopt en
niets meeneemt naar zijn eigen team, telt hier niet mee — en dat is met opzet.
