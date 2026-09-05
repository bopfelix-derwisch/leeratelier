#!/usr/bin/env python3
"""Zet de openstaande meldingen in de repo, zodat ze overal te lezen zijn.

De meldingen staan in sqlite op orin3. Een Claude Code-sessie op een telefoon of
in de cloud heeft die database niet -- die heeft alleen de repo. Dit script schrijft
daarom `ops/meldingen/openstaand.md` en zet dat in git, zodat de meldingen-agent
overal werkt: op orin3 leest hij de database, elders dit bestand.

Draait dagelijks via `ops/systemd/atelier-meldingen.timer`.

    python3 ops/meldingen-dump.py            # schrijf het bestand
    python3 ops/meldingen-dump.py --push     # en commit + push als er iets veranderde

Privacy
-------
`bezoeker_id` is een e-mailadres uit de Access-header. Dat gaat **niet** de repo in.
In het bestand staat een korte pseudoniem-hash plus het meldingnummer; wie werkelijk
achter een melding zit, is alleen op orin3 zelf op te zoeken. Zie besluit B12 over de
bewaartermijn en de privacytekst op de inlogpagina.

Alleen stdlib.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
DB = Path("/mnt/nvme/leeratelier/atelier.db")
UIT = HIER / "ops" / "meldingen" / "openstaand.md"


def pseudoniem(bezoeker_id: str) -> str:
    """Kort en stabiel, maar niet terug te rekenen naar een adres."""
    if not bezoeker_id:
        return "onbekend"
    return "bezoeker-" + hashlib.sha256(bezoeker_id.encode()).hexdigest()[:8]


def lees() -> list:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rijen = con.execute(
        "SELECT id, tijdstip, bezoeker_id, module_id, tekst, context FROM meldingen "
        "WHERE afgehandeld IS NULL OR afgehandeld=0 ORDER BY id").fetchall()
    con.close()
    return [dict(r) for r in rijen]


def schrijf(meldingen: list) -> str:
    nu = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    regels = [
        "# Openstaande meldingen",
        "",
        f"Bijgewerkt: {nu} &middot; automatisch gegenereerd door `ops/meldingen-dump.py`.",
        "Niet met de hand bijwerken; afvinken gebeurt in de database op orin3.",
        "",
        "E-mailadressen staan hier bewust niet in. Wie achter een melding zit, is alleen",
        "op orin3 zelf op te zoeken via het meldingnummer.",
        "",
    ]
    if not meldingen:
        regels += ["Er staat op dit moment niets open.", ""]
        return "\n".join(regels)

    regels += [f"**{len(meldingen)} open.** Beoordelen doe je met de agent `meldingen`;",
               "`ops/runbook.md` situatie 15 beschrijft de lus.", "", "---", ""]
    for m in meldingen:
        try:
            ctx = json.loads(m["context"] or "{}")
        except ValueError:
            ctx = {}
        regels += [
            f"## Melding {m['id']} &middot; `{m['module_id']}`",
            "",
            f"- **Wanneer:** {(m['tijdstip'] or '')[:16]}",
            f"- **Van:** {pseudoniem(m['bezoeker_id'])}",
            "",
            "**Wat de bezoeker schreef:**",
            "",
            "> " + (m["tekst"] or "").strip().replace("\n", "\n> "),
            "",
        ]
        if ctx:
            regels += ["**Context op dat moment:**", ""]
            for k, v in ctx.items():
                if v not in (None, "", False):
                    regels.append(f"- `{k}`: {v}")
            regels.append("")
        regels += [f"Module: `content/modules/{m['module_id']}/module.md`", "", "---", ""]
    return "\n".join(regels)


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=HIER, capture_output=True, text=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Openstaande meldingen naar de repo schrijven")
    p.add_argument("--push", action="store_true", help="commit en push als er iets veranderde")
    args = p.parse_args()

    if not DB.exists():
        print(f"database niet gevonden: {DB}", file=sys.stderr)
        return 1

    meldingen = lees()
    tekst = schrijf(meldingen)
    UIT.parent.mkdir(parents=True, exist_ok=True)
    oud = UIT.read_text(encoding="utf-8") if UIT.exists() else ""

    # De regel met het tijdstip verandert elke dag; dat alleen is geen wijziging.
    def zonder_kop(t: str) -> str:
        return "\n".join(r for r in t.split("\n") if not r.startswith("Bijgewerkt:"))

    veranderd = zonder_kop(oud) != zonder_kop(tekst)
    if not veranderd:
        print(f"{len(meldingen)} open, ongewijzigd sinds de vorige keer")
        return 0

    UIT.write_text(tekst, encoding="utf-8")
    pad = str(UIT.relative_to(HIER))
    print(f"{len(meldingen)} open, {pad} bijgewerkt")
    if not args.push:
        return 0

    # Alleen dit ene bestand. Draait onbewaakt; nooit andermans werk meecommitten.
    git("add", pad)
    if not git("diff", "--cached", "--quiet").returncode:
        print("niets te committen")
        return 0
    r = git("commit", "-m",
            f"ops: {len(meldingen)} openstaande melding(en) bijgewerkt\n\n"
            f"Automatisch door ops/meldingen-dump.py, zodat de meldingen-agent ze ook\n"
            f"buiten orin3 kan lezen. E-mailadressen blijven in de database.\n\n"
            f"Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>")
    if r.returncode:
        print(f"commit mislukt: {r.stderr.strip()[:200]}", file=sys.stderr)
        return 1
    r = git("push")
    if r.returncode:
        print(f"push mislukt: {r.stderr.strip()[:200]}", file=sys.stderr)
        return 1
    print("gepusht")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
