# Runbook — leeratelier

Doel: een tweede persoon lost een storing op zonder de bouwer. Af te maken in WP-18.

Het atelier is **permanent open en onbewaakt**. De beheerder is niet altijd bereikbaar. Alles hieronder
moet daarom uitvoerbaar zijn door iemand die het systeem niet gebouwd heeft.

## Snelle diagnose
```bash
curl -s http://127.0.0.1:8794/v1/gezondheid | python3 -m json.tool
systemctl status atelier-portaal atelier-bemiddelaar llama-klasmodel --no-pager
free -m | head -2 && df -h / /mnt/nvme | tail -2
```

## Situaties — nog uit te schrijven
- [ ] klasmodel weg → verwacht gedrag: alles valt terug op conserven, portaal blijft werken
- [ ] wachtrij loopt vol → drempels in sysmonitor, handmatig naar conserven schakelen
- [ ] dagbudget te snel op → waar `config/budget.yaml` staat en wat een veilige stap is
- [ ] RAG-index verouderd → herbouwcommando en hoe lang het duurt
- [ ] portaal onbereikbaar maar dienst draait → tunnel of Access
- [ ] module publiceren of terugzetten naar concept
- [ ] meldingen uit de "ik kom er niet uit"-knop afhandelen
- [ ] herstel na een reboot: welke units, in welke volgorde

## Tijdelijk: het portaal bekijken via Tailscale

Zolang WP-07 (Cloudflare Access) niet staat, is het portaal alleen binnen het tailnet te bekijken.
De dienst zelf blijft op `127.0.0.1`; Tailscale zet er een proxy voor.

```bash
sudo tailscale serve --bg --https=443 http://127.0.0.1:8793   # aanzetten
tailscale serve status                                        # controleren
sudo tailscale serve --https=443 off                          # uitzetten
```

Bereikbaar op **https://orin3.tail897ef4.ts.net/** voor apparaten in het tailnet.

**Dit is geen toegangsbeveiliging.** Binnen het tailnet is er geen inlog: iedereen deelt hetzelfde
budget en dezelfde naam, en wie een `Cf-Access-Authenticated-User-Email`-header meestuurt, is die
persoon. Het portaal zegt dat ook zelf in een banner. Zet dit uit zodra Access er staat, of eerder
als er iemand anders in het tailnet komt.

## Wat je nooit doet tijdens openingstijd
- een POC-repo aanraken
- de RAG-index herbouwen zonder aankondiging (K4 en spoor L worden er onvoorspelbaar van)
- het dagbudget verhogen om een klacht op te lossen; kijk eerst of het klasmodel wel draait
