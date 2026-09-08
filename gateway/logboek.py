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

    # Twee keer tikken op een trage telefoon is twee POST's, en een verversing na
    # het versturen is er nog een. Dat leverde in de praktijk drie identieke
    # meldingen op. Binnen dit venster geldt dezelfde tekst van dezelfde bezoeker
    # op dezelfde module als dezelfde melding. Zie V41.
    DUBBEL_VENSTER_MIN = 10

    def melding(self, bezoeker_id: str, module_id: str, tekst: str, context: dict) -> int:
        grens = (datetime.now(timezone.utc)
                 - timedelta(minutes=self.DUBBEL_VENSTER_MIN)).isoformat()
        bestaat = self.con.execute(
            "SELECT id FROM meldingen WHERE bezoeker_id=? AND module_id=? AND tekst=? "
            "AND tijdstip >= ? ORDER BY id DESC LIMIT 1",
            (bezoeker_id, module_id, tekst, grens)).fetchone()
        if bestaat:
            # Geen fout voor de bezoeker: die krijgt gewoon de bevestiging te zien.
            return int(bestaat["id"])

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

    def bezochte_modules(self, bezoeker_id: str) -> list:
        """Welke modules deze bezoeker geopend heeft, en wanneer voor het eerst."""
        rijen = self.con.execute(
            "SELECT module_id, MIN(tijdstip) AS eerste, COUNT(*) AS keer "
            "FROM logboek WHERE bezoeker_id=? AND module_id!='' "
            "GROUP BY module_id ORDER BY eerste", (bezoeker_id,)).fetchall()
        return [{"module_id": r["module_id"], "eerste": r["eerste"], "keer": r["keer"]}
                for r in rijen]

    # Onder dit aantal metingen is een p95 geen p95 maar het maximum: bij n <= 20
    # geeft int(n * 0.95) altijd de laatste index, en bepaalt een enkele uitschieter
    # dus in zijn eentje de waarde. Zie V35.
    P95_MINIMUM = 10
    P95_VENSTER_UREN = 24

    def latency_beeld(self, laatste: int = 50, venster_uren: int = P95_VENSTER_UREN,
                      minimum: int = P95_MINIMUM) -> dict:
        """Beeld van de recente antwoordtijden, voor de sysmonitor-drempel.

        Plan par. 8 zet warn op 60 s en crit op 120 s. Die drempels zijn in WP-01
        tegen de meting gehouden en bleken goed gekozen.

        Twee dingen die hier eerder misgingen (V35). De selectie had geen
        tijdvenster, dus een trage meting bleef de waarschuwing voeden tot er
        vijftig nieuwere antwoorden overheen waren geschoven -- op dit tempo
        maanden. En bij weinig metingen is de uitkomst het maximum, waardoor één
        losse aanroep een storing leek. Vandaar het venster en de ondergrens.

        Geeft ook terug welk model de traagste van die antwoorden gaf, zodat het
        advies niet naar een model hoeft te gokken.
        """
        grens = (datetime.now(timezone.utc) - timedelta(hours=venster_uren)).isoformat()
        rijen = self.con.execute(
            "SELECT latency_ms, model FROM logboek "
            "WHERE gelukt=1 AND latency_ms>0 AND tijdstip >= ? "
            "ORDER BY id DESC LIMIT ?", (grens, laatste)).fetchall()

        n = len(rijen)
        beeld = {"p95_ms": 0, "metingen": n, "minimum": minimum,
                 "venster_uren": venster_uren, "traagste_model": None}
        if n < minimum:
            # Te weinig om iets te beweren. Bewust 0: sysmonitor leest dat als
            # "geen oordeel" en niet als "snel".
            return beeld

        waarden = sorted(r["latency_ms"] for r in rijen)
        beeld["p95_ms"] = int(waarden[min(n - 1, int(n * 0.95))])
        traagste = max(rijen, key=lambda r: r["latency_ms"])
        beeld["traagste_model"] = traagste["model"] or None
        return beeld

    def p95_latency_ms(self, laatste: int = 50) -> int:
        """Alleen de p95 uit `latency_beeld`. Blijft bestaan voor bestaande aanroepers."""
        return self.latency_beeld(laatste=laatste)["p95_ms"]

    def ruim_op(self) -> int:
        """Verwijder logregels ouder dan de bewaartermijn. Draait dagelijks."""
        grens = (datetime.now(timezone.utc) - timedelta(days=self.inst.logboek_dagen)).isoformat()
        with transactie(self.con):
            cur = self.con.execute("DELETE FROM logboek WHERE tijdstip < ?", (grens,))
        return cur.rowcount or 0
