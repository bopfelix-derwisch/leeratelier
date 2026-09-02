# Toegang, capaciteit en permanent bedrijf

Volledige uitwerking: `plan-v0.3.md`, hoofdstuk 4. Hier het operationele deel.

## Kernidee
**Rantsoeneer het model, niet de deur.** Het lichte pad (pagina's, dashboards, live API-calls, conserven)
is onbeperkt. Alleen live modelantwoorden zijn schaars.

## Onbewaakt bedrijf
Permanent open terwijl de beheerder niet altijd bereikbaar is, betekent dat het atelier zonder ingrijpen
moet blijven werken:
- alle units `Restart=always`, `StartLimitIntervalSec=0`
- de bemiddelaar overleeft het wegvallen van een model
- conserven maken de hele route beschikbaar zonder enig model
- dagbudget reset automatisch om middernacht
- storingsbanner, automatisch gezet door sysmonitor
- eerlijke verwachting op de inlogpagina: *dit is een privé-lab van één persoon; storingen kunnen dagen duren*

Die laatste regel is geen zwaktebod. Verwachtingsmanagement is het goedkoopste beheersinstrument dat er
is, en voor deze doelgroep is het meteen een les.

## Budget
Waarden in `config/budget.yaml`. Nooit hardcoderen. De huidige waarden zijn **gerekend, niet gemeten** —
WP-01 vervangt ze.

## Logging
Besloten (B12): vragen worden gelogd, 90 dagen, doel en termijn op de inlogpagina. Dit is meteen materiaal
voor module K6: wie zelf gelogd wordt, begrijpt beter waarom logging in de eigen toepassing nodig is.
