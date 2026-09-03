"""Antwoordcache, trede 1 van de degradatieladder.

In een atelier stelt iedereen ongeveer dezelfde vragen. De tweede tot en met
twaalfde bezoeker krijgen het antwoord dus gratis, en dat is waar het dagbudget
vandaan komt dat zonder cache niet zou halen.

Over normaliseren: kleine letters, dubbele spaties weg, leestekens aan de randen weg.
Meer niet. Het contract in `gateway/README.md` is daar expliciet over, en met reden --
juist in module K4 zijn subtiele verschillen tussen twee vragen de les. Wie hier
agressiever normaliseert (stopwoorden weg, stammen), laat verschillende vragen op
elkaar lijken en maakt de module stuk.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from .db import transactie

_SPATIES = re.compile(r"\s+")
_RANDEN = re.compile(r"^[^\w]+|[^\w]+$")


def normaliseer(vraag: str) -> str:
    return _RANDEN.sub("", _SPATIES.sub(" ", vraag.strip().lower()))


def sleutel(vraag: str, module_id: str, model: str) -> str:
    ruw = f"{normaliseer(vraag)}|{module_id}|{model}"
    return hashlib.sha256(ruw.encode("utf-8")).hexdigest()


class Cache:
    def __init__(self, con: sqlite3.Connection, inst):
        self.con = con
        self.inst = inst

    def zoek(self, vraag: str, module_id: str, model: str):
        if not self.inst.cache_aan:
            return None
        grens = (datetime.now(timezone.utc) - timedelta(hours=self.inst.cache_uren)).isoformat()
        r = self.con.execute(
            "SELECT antwoord FROM cache WHERE sleutel=? AND aangemaakt>=?",
            (sleutel(vraag, module_id, model), grens)).fetchone()
        return r["antwoord"] if r else None

    def bewaar(self, vraag: str, module_id: str, model: str, antwoord: str) -> None:
        if not self.inst.cache_aan or not antwoord:
            return
        with transactie(self.con):
            self.con.execute(
                "INSERT OR REPLACE INTO cache (sleutel, module_id, model, antwoord, aangemaakt) "
                "VALUES (?, ?, ?, ?, ?)",
                (sleutel(vraag, module_id, model), module_id, model, antwoord,
                 datetime.now(timezone.utc).isoformat()))

    def ruim_op(self) -> int:
        """Verwijder verlopen antwoorden. Geeft terug hoeveel er weg zijn."""
        grens = (datetime.now(timezone.utc) - timedelta(hours=self.inst.cache_uren)).isoformat()
        with transactie(self.con):
            cur = self.con.execute("DELETE FROM cache WHERE aangemaakt < ?", (grens,))
        return cur.rowcount or 0
