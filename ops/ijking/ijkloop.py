#!/usr/bin/env python3
"""Draai de Nederlandse ijkset langs één model (WP-03).

Eén stuk werk, drie opbrengsten:
  1. selectieprocedure  — welk model wordt het klasmodel?
  2. conserven-voorraad — voorberekende antwoorden voor de degradatieladder
  3. lesmateriaal       — module K3 laat precies deze vergelijking zien

    python3 ijkloop.py --endpoint http://127.0.0.1:8081 --model-naam qwen3-8b
    python3 ijkloop.py --vergelijk ijkset-qwen3-8b-*.jsonl ijkset-qwen2.5-32b-*.jsonl

Alleen stdlib.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

SYSTEEM = (
    "Je bent een assistent voor Nederlandse overheidsprofessionals. "
    "Antwoord in het Nederlands, bondig, en zeg het als je iets niet zeker weet."
)


def geheugen_gebruikt_mb() -> int | None:
    try:
        uit = subprocess.run(["free", "-m"], capture_output=True, text=True,
                             timeout=5, check=True).stdout.splitlines()
        return int(uit[1].split()[2])
    except Exception:
        return None


def vraag_model(endpoint: str, vraag: str, max_tokens: int, timeout: int) -> dict:
    payload = json.dumps({
        "model": "local",
        "messages": [{"role": "system", "content": SYSTEEM},
                     {"role": "user", "content": vraag}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }).encode()
    verzoek = urllib.request.Request(
        f"{endpoint.rstrip('/')}/v1/chat/completions",
        data=payload, headers={"Content-Type": "application/json"})

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(verzoek, timeout=timeout) as resp:
            body = json.load(resp)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as fout:
        return {"ok": False, "fout": str(fout), "duur_s": round(time.perf_counter() - start, 2)}

    duur = time.perf_counter() - start
    antwoord = body.get("choices", [{}])[0].get("message", {}).get("content", "")
    gebruik = body.get("usage", {}) or {}
    uit_tokens = gebruik.get("completion_tokens")
    return {
        "ok": True,
        "antwoord": antwoord,
        "duur_s": round(duur, 2),
        "tokens_uit": uit_tokens,
        "tok_per_s": round(uit_tokens / duur, 1) if uit_tokens and duur else None,
        "tekens": len(antwoord),
    }


def loop(a: argparse.Namespace) -> int:
    ijkset = [json.loads(r) for r in open(a.ijkset, encoding="utf-8") if r.strip()]
    print(f"IJkset: {len(ijkset)} vragen · model: {a.model_naam} · endpoint: {a.endpoint}")
    print(f"Geheugen in gebruik vooraf: {geheugen_gebruikt_mb()} MB\n")

    uitpad = a.out or os.path.join(
        os.path.dirname(a.ijkset) or ".",
        f"ijking/ijkset-{a.model_naam}-{datetime.now():%Y-%m-%d}.jsonl")
    os.makedirs(os.path.dirname(uitpad) or ".", exist_ok=True)

    geslaagd, duren = 0, []
    with open(uitpad, "w", encoding="utf-8") as uit:
        for i, item in enumerate(ijkset, 1):
            print(f"[{i:>2}/{len(ijkset)}] {item['id']} ({item['domein']}) ", end="", flush=True)
            res = vraag_model(a.endpoint, item["vraag"], a.max_tokens, a.timeout)
            if res.get("ok"):
                geslaagd += 1
                duren.append(res["duur_s"])
                print(f"{res['duur_s']}s · {res['tekens']} tekens")
            else:
                print(f"MISLUKT ({res.get('fout', '')[:50]})")
            uit.write(json.dumps({
                "model": a.model_naam, "endpoint": a.endpoint,
                "tijdstip": datetime.now().isoformat(timespec="seconds"),
                **item, **res,
            }, ensure_ascii=False) + "\n")

    print(f"\nGeslaagd: {geslaagd}/{len(ijkset)}")
    if duren:
        duren.sort()
        print(f"Mediaan: {duren[len(duren)//2]}s · traagste: {duren[-1]}s "
              f"· totaal: {round(sum(duren))}s")
    print(f"Geheugen in gebruik achteraf: {geheugen_gebruikt_mb()} MB")
    print(f"\nGeschreven naar {uitpad}")
    print("\nBeoordeel de antwoorden handmatig tegen het veld 'verwacht' en 'let_op'.")
    print("Vraag ijk-20 is de belangrijkste: een model dat daar stellig antwoordt zonder")
    print("bron te noemen, faalt — hoe goed de rest ook is.")
    return 0


def vergelijk(paden: list[str]) -> int:
    """Zet meerdere runs naast elkaar. Dit is het skelet van module K3."""
    bestanden: list[str] = []
    for p in paden:
        bestanden.extend(sorted(glob.glob(p)))
    if not bestanden:
        print("geen bestanden gevonden"); return 1

    runs: dict[str, dict[str, dict]] = {}
    for pad in bestanden:
        for regel in open(pad, encoding="utf-8"):
            if not regel.strip():
                continue
            r = json.loads(regel)
            runs.setdefault(r["model"], {})[r["id"]] = r

    modellen = list(runs)
    vraag_ids = sorted({vid for m in runs.values() for vid in m})

    breedte = max(len(m) for m in modellen) + 2
    print(f"\n{'vraag':<10}" + "".join(f"{m:<{breedte}}" for m in modellen))
    print("-" * (10 + breedte * len(modellen)))
    for vid in vraag_ids:
        rij = f"{vid:<10}"
        for m in modellen:
            r = runs[m].get(vid, {})
            cel = f"{r.get('duur_s', '-')}s/{r.get('tekens', '-')}t" if r.get("ok") else "MISLUKT"
            rij += f"{cel:<{breedte}}"
        print(rij)

    print()
    for m in modellen:
        gelukt = [r for r in runs[m].values() if r.get("ok")]
        duren = sorted(r["duur_s"] for r in gelukt)
        if not duren:
            print(f"{m:<{breedte}} geen geslaagde antwoorden"); continue
        print(f"{m:<{breedte}} {len(gelukt)}/{len(runs[m])} geslaagd · "
              f"mediaan {duren[len(duren)//2]}s · totaal {round(sum(duren))}s")
    print("\nDeze tabel is de kern van module K3. Zet er in de module het geheugengebruik")
    print("en de modelgrootte naast: dan wordt zichtbaar dat tokengeneratie op deze machine")
    print("bandbreedte-gebonden is, en niet rekenkracht-gebonden.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="IJkset langs een model draaien")
    p.add_argument("--endpoint", default="http://127.0.0.1:8081")
    p.add_argument("--model-naam", default="onbekend")
    p.add_argument("--ijkset", default=os.path.join(os.path.dirname(__file__), "..", "ijkset-nl.jsonl"))
    p.add_argument("--max-tokens", type=int, default=400)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--out", default=None)
    p.add_argument("--vergelijk", nargs="+", metavar="BESTAND",
                   help="zet eerdere runs naast elkaar in plaats van te meten")
    a = p.parse_args()

    if a.vergelijk:
        return vergelijk(a.vergelijk)
    a.ijkset = os.path.normpath(a.ijkset)
    return loop(a)


if __name__ == "__main__":
    sys.exit(main())
