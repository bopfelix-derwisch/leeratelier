#!/usr/bin/env bash
# WP-02: hangt MoE-decode op deze chip en deze build?
#
# Achtergrond: ggml-org/llama.cpp issue #19219 meldt dat MoE-modellen op Jetson Orin AGX
# (SM87, compute capability 8.7) blijven hangen bij decode op alle builds na b7309 (dec 2025).
# Het model laadt wel, maar er komen nooit tokens. Deze machine draait build 8117.
# Dense modellen waren niet getroffen.
#
# Gebruik:  bash moe_check.sh /mnt/nvme/nvme/models/<moe-model>.gguf [poort]
#
# Uitkomst: "GESLAAGD" -> MoE werkt, Gemma 4 26B-A4B is een serieuze kandidaat.
#           "HANGT"    -> dense blijft de weg; noteer dat in het besluitenlog.
#
# LET OP: bewerk dit bestand niet terwijl het draait. Bash leest een script
# incrementeel; een wijziging halverwege verschuift de offsets en levert een
# syntaxfout op een regel die prima is. Overkomen op 2026-09-02.

set -u
MODEL="${1:?geef het pad naar een MoE-GGUF}"
POORT="${2:-8099}"
TIMEOUT="${TIMEOUT:-120}"          # seconden voor de generatie zelf
LAADVENSTER="${LAADVENSTER:-420}"  # seconden om te wachten tot /health antwoordt
LOG="$(mktemp)"

command -v llama-server >/dev/null || { echo "llama-server niet gevonden in PATH"; exit 2; }
[ -f "$MODEL" ] || { echo "model niet gevonden: $MODEL"; exit 2; }

echo "Model:   $MODEL"
echo "Build:   $(llama-server --version 2>&1 | grep -m1 '^version:')"
echo "Poort:   $POORT   generatie-timeout: ${TIMEOUT}s   laadvenster: ${LAADVENSTER}s"
echo "Geheugen vooraf:"; free -m | head -2
echo

llama-server --model "$MODEL" --host 127.0.0.1 --port "$POORT" \
             --ctx-size 2048 --n-gpu-layers 99 --threads 4 >"$LOG" 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null' EXIT

echo -n "wachten tot het model geladen is"
for _ in $(seq 1 $((LAADVENSTER / 2))); do
  if curl -sf "http://127.0.0.1:$POORT/health" >/dev/null 2>&1; then echo " -> geladen"; break; fi
  echo -n "."; sleep 2
done

if ! curl -sf "http://127.0.0.1:$POORT/health" >/dev/null 2>&1; then
  echo; echo "RESULTAAT: LADEN MISLUKT (geen /health binnen ${LAADVENSTER}s)"
  tail -20 "$LOG"; exit 1
fi

echo "een korte generatie proberen (dit is waar de bug toeslaat)..."
START=$(date +%s)
ANTWOORD=$(curl -sf --max-time "$TIMEOUT" \
  "http://127.0.0.1:$POORT/v1/chat/completions" \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Noem drie kleuren."}],"max_tokens":24}' 2>&1)
RC=$?
DUUR=$(( $(date +%s) - START ))

echo; echo "Geheugen tijdens:"; free -m | head -2; echo
if [ $RC -ne 0 ] || [ -z "$ANTWOORD" ]; then
  echo "RESULTAAT: HANGT — geen tokens binnen ${DUUR}s."
  echo "Het model laadde wel. Dit is het gedrag uit issue #19219."
  echo "Vervolg: check of het issue gesloten is, of blijf bij dense modellen."
  tail -20 "$LOG"
  exit 1
fi

echo "RESULTAAT: GESLAAGD — antwoord in ${DUUR}s."
echo "$ANTWOORD" | head -c 400; echo
echo
echo "MoE werkt op deze build. Gemma 4 26B-A4B (3,8B actief van 25,2B) is nu de sterkste"
echo "kandidaat voor deze machine: 4B-snelheid bij veel hogere kwaliteit."
