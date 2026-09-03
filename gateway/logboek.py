"""Logboek en meldingen.

Besluit B12: vragen worden gelogd, 90 dagen, doel en termijn op de inlogpagina.
De bewaartermijn staat in `config/budget.yaml` en is gelijk aan die van
`history.jsonl` van sysmonitor -- één termijn op de machine is makkelijker uit te
leggen dan twee.

Dit is meteen materiaal voor module K6: wie zelf gelogd wordt, begrijpt beter waarom
logging in de eigen toepassing nodig is, en wat ervoor geregeld moet zijn.

Meldingen komen van de "ik kom er niet uit"-knop. Die vangt context, want de beheerder
is niet altijd bereikbaar en een melding zonder context kost een heen-en-weer dat
dagen kan duren.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone

from .db import transactie


class Logboek:
    def __init__(self, con: sqlite3.Connection, inst):
        self.con = con
        self.inst = inst

    def schrijf(self, bezoeker_id: str, module_id: str, vraag: str, model: str,
                bron: str, latency_ms: int, beurten: int, gelukt: bool) -> None:
        if not self.inst.logboek_aan:
            return
        with transactie(self.con):
            self.con.execute(
                "INSERT INTO logboek (tijdstip, bezoeker_id, module_id, vraag, model, "
                "bron, latency_ms, beurten, gelukt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), bezoeker_id, module_id, vraag,
                 model, bron, int(latency_ms), int(beurten), 1 if gelukt else 0))

    def melding(self, bezoeker_id: str, module_id: str, tekst: str, context: dict) -> int:
        with transactie(self.con):
            cur = self.con.execute(
                "INSERT INTO meldingen (tijdstip, bezoeker_id, module_id, tekst, context) "
                "VALUES (?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), bezoeker_id, module_id, tekst,
                 json.dumps(context or {}, ensure_ascii=False)))
        return int(cur.lastrowid)

    def open_meldingen(self) -> int:
        r = self.con.execute(
            "SELECT COUNT(*) AS n FROM meldingen WHERE afgehandeld=0").fetchone()
        return int(r["n"])

    def p95_latency_ms(self, laatste: int = 50) -> int:
        """p95 over de recente geslaagde antwoorden, voor de sysmonitor-drempel.

        Plan par. 8 zet warn op 60 s en crit op 120 s. Die drempels zijn in WP-01
        tegen de meting gehouden en bleken goed gekozen.
        """
        rijen = self.con.execute(
            "SELECT latency_ms FROM logboek WHERE gelukt=1 AND latency_ms>0 "
            "ORDER BY id DESC LIMIT ?", (laatste,)).fetchall()
        waarden = sorted(r["latency_ms"] for r in rijen)
        if not waarden:
            return 0
        return int(waarden[min(len(waarden) - 1, int(len(waarden) * 0.95))])

    def ruim_op(self) -> int:
        """Verwijder logregels ouder dan de bewaartermijn. Draait dagelijks."""
        grens = (datetime.now(timezone.utc) - timedelta(days=self.inst.logboek_dagen)).isoformat()
        with transactie(self.con):
            cur = self.con.execute("DELETE FROM logboek WHERE tijdstip < ?", (grens,))
        return cur.rowcount or 0
