#!/usr/bin/env python3
"""Inspecteer de RAG-index (WP-09a).

Beantwoordt de vraag die het hele lesmateriaal raakt: hoeveel zit er werkelijk in?
`vectors.npy` is 33 KB. Bij bge-m3 (1024 dimensies, fp32) is dat ongeveer 8 fragmenten.
Als dat klopt, beantwoordt de vergunningen-chatbot vragen uit een handvol stukken tekst
van juni. Dat is te dun voor lesgebruik, maar uitstekend materiaal voor module K4.

    python3 rag_inspect.py --dir /mnt/nvme/geluidsmeter/data/rag

Leest de numpy-header handmatig, zodat numpy niet nodig is als het er niet staat.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from datetime import datetime, timezone


def lees_npy_header(pad: str) -> dict:
    """Lees vorm en dtype uit een .npy-bestand zonder numpy te importeren."""
    with open(pad, "rb") as f:
        magic = f.read(6)
        if magic != b"\x93NUMPY":
            raise ValueError(f"{pad} is geen .npy-bestand")
        major = f.read(1)[0]
        f.read(1)  # minor
        lengte = int.from_bytes(f.read(2 if major == 1 else 4), "little")
        header = f.read(lengte).decode("latin1").strip()
        meta = ast.literal_eval(header)
        data_offset = f.tell()

    bestandsgrootte = os.path.getsize(pad)
    return {
        "vorm": meta["descr"] and meta["shape"],
        "dtype": meta["descr"],
        "fortran_order": meta.get("fortran_order", False),
        "header_bytes": data_offset,
        "data_bytes": bestandsgrootte - data_offset,
        "bestand_bytes": bestandsgrootte,
    }


def lees_chunks(pad: str) -> dict:
    regels, tekens, bronnen = 0, 0, {}
    voorbeeld = None
    with open(pad, encoding="utf-8") as f:
        for regel in f:
            regel = regel.strip()
            if not regel:
                continue
            regels += 1
            try:
                rec = json.loads(regel)
            except json.JSONDecodeError:
                continue
            tekst = rec.get("text") or rec.get("chunk") or rec.get("content") or ""
            tekens += len(tekst)
            bron = rec.get("source") or rec.get("bron") or rec.get("url") or "onbekend"
            bronnen[bron] = bronnen.get(bron, 0) + 1
            if voorbeeld is None:
                voorbeeld = {"velden": sorted(rec.keys()), "tekstlengte": len(tekst)}
    return {
        "fragmenten": regels,
        "tekens_totaal": tekens,
        "tekens_gemiddeld": round(tekens / regels) if regels else 0,
        "bronnen": bronnen,
        "eerste_record": voorbeeld,
    }


def oordeel(aantal: int) -> str:
    if aantal == 0:
        return "LEEG. De chatbot heeft geen enkel fragment om uit te putten."
    if aantal < 50:
        return (
            f"ZEER DUN ({aantal} fragmenten). Dit is geen kennisbank maar een handvol tekst. "
            "Blokkerend voor K4 en spoor L: herbouwen en vergroten (WP-09b) voordat dit lesmateriaal wordt."
        )
    if aantal < 500:
        return f"DUN ({aantal} fragmenten). Bruikbaar om te demonstreren, te smal om op te vertrouwen."
    return f"REDELIJK ({aantal} fragmenten). Controleer wel de bouwdatum en de dekking per bron."


def main() -> int:
    p = argparse.ArgumentParser(description="Inspecteer de RAG-index")
    p.add_argument("--dir", default="/mnt/nvme/geluidsmeter/data/rag")
    p.add_argument("--vectors", default="vectors.npy")
    p.add_argument("--chunks", default="chunks.jsonl")
    p.add_argument("--dim", type=int, default=1024, help="embedding-dimensie van bge-m3")
    a = p.parse_args()

    vpad = os.path.join(a.dir, a.vectors)
    cpad = os.path.join(a.dir, a.chunks)

    print(f"RAG-inspectie · {a.dir}\n" + "=" * 60)

    aantal_vectoren = None
    if os.path.exists(vpad):
        try:
            info = lees_npy_header(vpad)
            print(f"\n{a.vectors}")
            print(f"  vorm            {info['vorm']}")
            print(f"  dtype           {info['dtype']}")
            print(f"  bestandsgrootte {info['bestand_bytes']:,} bytes")
            if isinstance(info["vorm"], tuple) and info["vorm"]:
                aantal_vectoren = info["vorm"][0]
        except Exception as fout:
            print(f"  header onleesbaar: {fout}")
            grootte = os.path.getsize(vpad)
            geschat = grootte // (a.dim * 4)
            print(f"  schatting bij {a.dim} dim fp32: ~{geschat} vectoren")
            aantal_vectoren = geschat
        mtime = datetime.fromtimestamp(os.path.getmtime(vpad), timezone.utc)
        ouderdom = (datetime.now(timezone.utc) - mtime).days
        print(f"  laatst gewijzigd {mtime:%Y-%m-%d} ({ouderdom} dagen geleden)")
    else:
        print(f"\n{a.vectors} NIET GEVONDEN")

    if os.path.exists(cpad):
        c = lees_chunks(cpad)
        print(f"\n{a.chunks}")
        print(f"  fragmenten      {c['fragmenten']}")
        print(f"  tekens totaal   {c['tekens_totaal']:,}")
        print(f"  gemiddeld       {c['tekens_gemiddeld']} tekens per fragment")
        print(f"  velden          {c['eerste_record']['velden'] if c['eerste_record'] else '-'}")
        print(f"  bronnen         {len(c['bronnen'])}")
        for bron, n in sorted(c["bronnen"].items(), key=lambda x: -x[1])[:10]:
            print(f"    {n:>4}  {bron[:70]}")
        if aantal_vectoren is None:
            aantal_vectoren = c["fragmenten"]
        elif aantal_vectoren != c["fragmenten"]:
            print(f"\n  LET OP: {aantal_vectoren} vectoren maar {c['fragmenten']} fragmenten. "
                  "Die horen gelijk te zijn.")
    else:
        print(f"\n{a.chunks} NIET GEVONDEN")

    print("\n" + "=" * 60)
    print("OORDEEL: " + oordeel(aantal_vectoren or 0))
    print("\nNoteer de uitkomst in spec/05-besluitenlog.md en verwerk het aantal in module K4,")
    print("proef 2 — daar wordt de bezoeker geacht de rand van de index zelf te vinden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
