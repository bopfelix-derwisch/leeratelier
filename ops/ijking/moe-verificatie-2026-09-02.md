# MoE-verificatie WP-02 — 2026-09-02

Hangt Mixture-of-Experts-decode op deze chip en deze build? Het plan (§5.2) plant er niet op tot dit
schriftelijk beantwoord is, omdat MoE op papier het beste is dat deze machine kan draaien.

**Antwoord: nee, het hangt niet. MoE werkt — en is ruim vijf keer sneller dan het huidige showmodel.**

---

## 1. Het issue: gesloten, maar niet zoals het lijkt

`ggml-org/llama.cpp` issue **#19219** — *"MoE model decode hangs on Jetson Orin AGX (SM87) since b7309"*.

| | |
|---|---|
| Geopend | 2026-01-30 |
| Gesloten | 2026-03-29, **`state_reason: not_planned`**, label **`stale`** |
| Reacties | 19 |

Het issue is dus **automatisch dichtgevallen na veertien dagen stilte**, niet opgelost verklaard. Wie
alleen naar de status kijkt, trekt de verkeerde conclusie. De discussie zelf is wél afgerond:

1. **De oorzaak is niet MoE.** Een bisect met `llama-server` wees commit `a83c73a18` aan
   ("[CUDA] Reduce CPU-side stalls due to the CUDA command buffer being full", #19042). Die zet
   `CUDA_SCALE_LAUNCH_QUEUES=4x` voor multi-GPU pipeline-parallellisme. Op Jetson met unified memory
   loopt de CUDA-commandbuffer daardoor vol: `strace` liet zien dat de submit-`ioctl` na ~7500 geslaagde
   submissies eindeloos `EAGAIN` teruggeeft. MoE-modellen waren simpelweg de zwaarste belasting en dus
   de eerste die het raakten; dense modellen bleven onder de drempel.
2. **De revert is gemerged.** PR **#19227** haalde de env-var weer weg; ggerganov merge-de die op
   2026-02-03.
3. **NVIDIA bevestigde een JetPack-bug.** Op 2026-02-11 meldde `gaugarg-nv` dat het CUDA-team de fout
   reproduceerde in de Jetson-softwarestack en dat de fix in de volgende JetPack-release zit.
4. Een tweede AGX Orin-gebruiker draaide Qwen3-30B-A3B Q4_K_M op b7860 zonder problemen.

## 2. Wat dat betekent voor deze machine

| Controle | Uitkomst |
|---|---|
| `strings llama-server \| grep CUDA_SCALE_LAUNCH_QUEUES` | **geen treffer** in beide binaries (`/usr/local/bin` en `~/llama.cpp/build/bin`) — de revert zit in build 8117 |
| JetPack / L4T | **R36.4.7**, GCID 42132812, 18-09-2025 |
| Kernel | **5.15.148-tegra** |

De trigger is dus weg uit onze build. Maar de JetPack op deze machine is **exact die van de melder**, en
de onderliggende fout die NVIDIA repareerde zit hier dus nog steeds.

> **Staand risico bij elke llama.cpp-upgrade.** Zodra een toekomstige build `CUDA_SCALE_LAUNCH_QUEUES`
> opnieuw introduceert — en gaugarg-nv gaf aan dat te willen zodra JetPack bijgewerkt is — hangt deze
> machine opnieuw, tot JetPack bijgewerkt wordt. Controleer na elke upgrade met de `strings`-regel
> hierboven. Dit is vondst **V5** in `spec/05-besluitenlog.md`.

## 3. De proef

Model: **Qwen3-30B-A3B-Instruct-2507 Q4_K_M** (18,4 GB, 30B parameters waarvan ~3B actief per token) —
bewust hetzelfde model en dezelfde quantisatie als in het issue-rapport, voor maximale bewijswaarde.
Gedownload naar `/mnt/nvme/nvme/models/qwen3-30b-a3b/`, niet naar `/`.

```
$ bash ops/ijking/moe_check.sh /mnt/nvme/nvme/models/qwen3-30b-a3b/Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf
Build:   version: 8117 (b908baf18)
RESULTAAT: GESLAAGD — antwoord in 1s.
{"choices":[{"finish_reason":"stop","message":{"content":"Blauw, groen en rood."}}],
 "system_fingerprint":"b8117-b908baf18","usage":{"completion_tokens":11}}
```

Decode produceert tokens, direct, in correct Nederlands. Geen hang.

## 4. Hoe snel het is — en dat is de eigenlijke vondst

Zelfde meetopstelling als WP-01 (`meet.py`, `max_tokens` 200, dezelfde prompt), zodat de getallen naast
elkaar te leggen zijn.

| | dense showmodel<br>Qwen2.5-32B Q4_K_M | MoE<br>Qwen3-30B-A3B Q4_K_M | verhouding |
|---|---:|---:|---:|
| bestandsgrootte | 19,0 GB | 18,4 GB | gelijk |
| actieve parameters | 32 B | ~3 B | **1 : 10** |
| tok/s per stroom (c=1) | 6,48 | **35,13** | **5,4×** |
| p50 (c=1) | 24,06 s | **4,32 s** | **5,6× sneller** |
| p50 (c=2) | 27,18 s | **7,72 s** | 3,5× sneller |
| doorzet (c=1) | 2,6 /min | **13,2 /min** | 5,1× |
| doorzet (c=2) | 4,3 /min | **15,8 /min** | 3,7× |
| tijd tot eerste teken (c=1) | 0,20 s | 0,05 s | 4× |
| GPU-bezetting | 94–96% | 87–88% | minder verzadigd |

De belofte uit plan §5.2 — *"4B-snelheid bij de kwaliteit van iets veel groters"* — is hiermee gemeten,
niet aangenomen. Bij vrijwel identieke bestandsgrootte levert het MoE-model **vijf keer** zoveel doorzet.
Dat het bandbreedte-argument uit §5.1 klopt, blijkt juist hier: er wordt per token maar een tiende van de
gewichten gelezen, en precies dat is wat op deze machine schaars is.

## 5. De rem: geheugen, niet snelheid

De eerste twee pogingen faalden, en niet op de bug:

```
ggml_backend_cuda_buffer_type_alloc_buffer: allocating 17524.43 MiB on device 0:
  cudaMalloc failed: out of memory
NvMapMemAllocInternalTagged: 1075072515 error 12
```

`free` meldde op dat moment 29,8 GB "available", maar daarvan zat 18 GB in page-cache. **NvMap kan die
cache niet opeisen**; de allocatie moet uit werkelijk vrij geheugen komen. Na `sync` en
`echo 3 > /proc/sys/vm/drop_caches` (30,2 GB echt vrij) laadde het model wel. De draaiende diensten op
`:8080` en `:8082` merkten daar niets van — beide bleven 200 antwoorden.

Met beide modellen tegelijk geladen stond de machine op **47,2 GB gebruikt en 499 MB vrij**. Coëxistentie
is dus technisch aangetoond, maar met minder dan een gigabyte marge. Voor een dienst die permanent en
**onbewaakt** open staat is dat geen werkbare marge: de eerstvolgende allocatie van wat dan ook faalt.

**Praktische regel voor deze machine:** twee modellen van elk ~19 GB passen niet naast elkaar. Er moet
gekozen worden.

## 6. Besluit dense versus MoE

MoE is niet alleen mogelijk maar duidelijk superieur op deze hardware. De vraag is niet meer óf, maar in
welke opstelling. Drie varianten, met de consequenties:

| Variant | Geheugen | Gevolg |
|---|---:|---|
| **A. MoE vervangt het showmodel**, klasmodel wordt een klein dens 8B | 18,4 + ~5 + 1,1 ≈ **25 GB** | ruime marge, showmodel 5× sneller, plan-structuur blijft intact. **Aanbevolen.** |
| B. Huidige opstelling houden, MoE niet gebruiken | 19 + ~5 + 1,1 ≈ 25 GB | laat een factor vijf liggen zonder reden |
| C. MoE naast het 32B-showmodel | ≈ 47 GB, 0,5 GB vrij | niet doen bij onbewaakt bedrijf |

**Advies: variant A.** Dat raakt besluit **B9** ("klasmodel apart van showmodel") niet in zijn opzet — er
blijven twee modellen — maar wel in de invulling: het showmodel wordt Qwen3-30B-A3B in plaats van
Qwen2.5-32B. Het raakt ook het budget uit WP-01, dat op 2,6–4,3 antwoorden per minuut gebaseerd is; met
variant A wordt dat 13–16 per minuut en is 300 beurten per dag ruim aan de veilige kant.

**Dit is een besluit voor de eigenaar, niet voor de meting.** Vandaar dat `config/modellen.yaml` nu
`moe_status.werkt_op_deze_build: true` bevat met de meetgegevens, maar `showmodel` nog ongewijzigd op
Qwen2.5-32B staat. Variant A doorvoeren is werk voor WP-03/WP-04.

## 7. Nog open

- **Gemma 4 26B-A4B**, de kandidaat uit plan §5.3, is niet getest: er is onder de verwachte naam geen
  GGUF-repository gevonden. Qwen3-30B-A3B vervult dezelfde rol en is bovendien sterker in het Nederlands.
  Meenemen in WP-03.
- **Kwaliteit is niet gemeten**, alleen snelheid. Of dit model inhoudelijk beter is dan het huidige
  showmodel bepaalt de ijkset in WP-03.
- De download staat op `/mnt/nvme/nvme/models/qwen3-30b-a3b/` (18,4 GB). Bij variant B kan die weg.

## 8. Wat er aan het gereedschap veranderd is

- `moe_check.sh` toonde bij `Build:` de eerste stderr-regel (`ggml_cuda_init: found 1 CUDA devices`)
  in plaats van het buildnummer, omdat `head -1` de verkeerde regel pakte. Nu `grep -m1 '^version:'` —
  juist bij dit werkpakket is het buildnummer het bewijs.
- Het laadvenster stond hard op 120 s. Een model van 18,4 GB laadt daar niet binnen; nu instelbaar via
  `LAADVENSTER`, standaard 420 s.
- Waarschuwing in de kop toegevoegd: **bewerk dit script niet terwijl het draait.** De eerste run liep
  stuk op een syntaxfout op regel 40 omdat het bestand tijdens uitvoering gewijzigd werd; bash leest een
  script incrementeel en de offsets verschoven. De regel zelf was correct.
