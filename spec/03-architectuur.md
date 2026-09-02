# Architectuur

Volledige uitwerking en diagram: `plan-v0.3.md`, hoofdstuk 8.
Contracten: `gateway/README.md` (bemiddelaar) en `app/README.md` (portaal).

```
bezoeker --Cloudflare Access--> portaal :8793 --> bemiddelaar :8794 --+--> klasmodel :8081
                                                                     +--> showmodel :8080
                                                                     +--> embeddings :8082
                                                                     +--> conserven (bestanden)
POC's (:8792 :8000 :8788 :8795) blijven ongewijzigd.
```

Uitgangspunt: **dunne laag naast de POC's, niet erin.** Op interactieniveau 1 raakt geen bezoeker ooit
een POC-repo aan, dus dit is goed vol te houden.

Poorten 8793 en 8794 zijn vrij; 8081 is leeg sinds `derwisch_local-nemo` disabled is.
Nieuwe diensten binden op `127.0.0.1` — de tunnel praat lokaal.
