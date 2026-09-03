#!/usr/bin/env python3
"""Genereer conserven uit een ijkset-run (WP-05).

Conserven zijn voorberekende antwoorden. Ze vlakken de piek af -- in een atelier
stelt iedereen ongeveer dezelfde vragen -- en ze houden de hele route beschikbaar
terwijl er geen model draait. Het atelier staat permanent en onbewaakt open; zonder
conserven is een weggevallen model gelijk aan een gesloten atelier.

De bron is een echte ijkset-run, niet een bedachte tekst: wat het klasmodel werkelijk
antwoordde. Daardoor is een conserf geen ander soort antwoord dan een live antwoord,
alleen eerder gegeven -- en het portaal labelt het zichtbaar als voorberekend.

    python3 ops/maak-conserven.py \\
        --ijkset ops/ijking/ijkset-qwen3-8b-2026-09-02.jsonl \\
        --module k04-wanneer-klopt-het-niet \\
        --domeinen vergunningen meta

De uitvoer staat in .gitignore: conserven zijn afgeleid, geen bron.
Alleen stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent

_SPATIES = re.compile(r"\s+")
_RANDEN = re.compile(r"^[^\w]+|[^\w]+$")


def normaliseer(vraag: str) -> str:
    """Zelfde regel als gateway/cache.py. Wijkt die af, dan mist elk conserf."""
    return _RANDEN.sub("", _SPATIES.sub(" ", vraag.strip().lower()))


def main() -> int:
    p = argparse.ArgumentParser(description="Conserven bouwen uit een ijkset-run")
    p.add_argument("--ijkset", required=True, help="ops/ijking/ijkset-<model>-<datum>.jsonl")
    p.add_argument("--module", required=True, help="module-id, gelijk aan de mapnaam")
    p.add_argument("--domeinen", nargs="*", default=None,
                   help="alleen deze domeinen; standaard alles")
    p.add_argument("--uit", default=None)
    a = p.parse_args()

    pad = Path(a.ijkset)
    if not pad.exists():
        print(f"ijkset niet gevonden: {pad}", file=sys.stderr)
        return 2

    rijen = [json.loads(r) for r in pad.open(encoding="utf-8") if r.strip()]
    gekozen = [r for r in rijen
               if r.get("ok") and r.get("antwoord")
               and (a.domeinen is None or r.get("domein") in a.domeinen)]
    if not gekozen:
        print("geen bruikbare antwoorden in deze run", file=sys.stderr)
        return 1

    model = gekozen[0].get("model", "onbekend")
    data = {
        "module_id": a.module,
        "gegenereerd_op": gekozen[0].get("tijdstip", "")[:10],
        "model": model,
        "herkomst": str(pad),
        "antwoorden": [
            {"vraag_genormaliseerd": normaliseer(r["vraag"]),
             "antwoord": r["antwoord"],
             "bron_labels": [f"ijkset {r['id']}"]}
            for r in gekozen
        ],
    }

    uit = Path(a.uit) if a.uit else WORTEL / "content" / "conserven" / f"{a.module}.json"
    uit.parent.mkdir(parents=True, exist_ok=True)
    uit.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(data['antwoorden'])} conserven -> {uit}")
    for x in data["antwoorden"]:
        print("  -", x["vraag_genormaliseerd"][:72])
    print("\nHerlaad de bemiddelaar om ze op te pikken:")
    print("  sudo systemctl restart atelier-bemiddelaar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
