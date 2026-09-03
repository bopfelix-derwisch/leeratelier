"""Sqlite-opslag voor de bemiddelaar: budget, logboek, cache en meldingen.

Vier tabellen, geen ORM, stdlib `sqlite3`. Het schema staat in `gateway/README.md`
en wordt hier letterlijk gevolgd.

De database staat op `/mnt/nvme/leeratelier/atelier.db`, niet op `/`: die schijf zit
op 82 procent en een volgelopen rootschijf legt de hele machine plat.

Over threads: elke aanroeper vraagt een eigen verbinding op. Sqlite laat dat toe zolang
verbindingen niet tussen threads gedeeld worden, en dat gebeurt hier niet -- FastAPI
draait de schrijvers in een threadpool.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS verbruik (
  bezoeker_id TEXT, datum TEXT, beurten INTEGER DEFAULT 0,
  gereserveerd INTEGER DEFAULT 0, PRIMARY KEY (bezoeker_id, datum));

CREATE TABLE IF NOT EXISTS logboek (
  id INTEGER PRIMARY KEY, tijdstip TEXT, bezoeker_id TEXT, module_id TEXT,
  vraag TEXT, model TEXT, bron TEXT, latency_ms INTEGER, beurten INTEGER,
  gelukt INTEGER);

CREATE TABLE IF NOT EXISTS cache (
  sleutel TEXT PRIMARY KEY, module_id TEXT, model TEXT,
  antwoord TEXT, aangemaakt TEXT);

CREATE TABLE IF NOT EXISTS meldingen (
  id INTEGER PRIMARY KEY, tijdstip TEXT, bezoeker_id TEXT, module_id TEXT,
  tekst TEXT, context TEXT, afgehandeld INTEGER DEFAULT 0);

CREATE INDEX IF NOT EXISTS idx_logboek_tijdstip ON logboek(tijdstip);
CREATE INDEX IF NOT EXISTS idx_cache_aangemaakt ON cache(aangemaakt);
"""


def _open(pad: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(pad), timeout=10.0)
    con.row_factory = sqlite3.Row
    # WAL laat lezers doorgaan terwijl er geschreven wordt. Het atelier leest
    # (budgetmeter, gezondheid) veel vaker dan het schrijft.
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=10000")
    con.executescript(SCHEMA)
    con.commit()
    return con


class Verbinding:
    """Eén sqlite-verbinding per thread, naar hetzelfde bestand.

    Sqlite weigert een verbinding te gebruiken vanuit een andere thread dan waarin
    hij gemaakt is, en FastAPI draait de schrijvers via `asyncio.to_thread` in een
    threadpool. Een gedeelde verbinding werkt dus in een test met één thread en
    valt om zodra er echt verkeer is -- precies het soort fout dat pas in productie
    zichtbaar wordt.

    WAL maakt dit goedkoop: meerdere lezers en één schrijver tegelijk, zonder dat
    de lezers wachten.
    """

    def __init__(self, pad: Path):
        self.pad = Path(pad)
        if str(self.pad) != ":memory:":
            self.pad.parent.mkdir(parents=True, exist_ok=True)
        self._lokaal = threading.local()
        self._alle: list = []
        self._slot = threading.Lock()
        if str(self.pad) != ":memory:":
            _open(self.pad).close()      # schema meteen aanleggen

    @property
    def _con(self) -> sqlite3.Connection:
        con = getattr(self._lokaal, "con", None)
        if con is None:
            con = _open(self.pad)
            self._lokaal.con = con
            with self._slot:
                self._alle.append(con)
        return con

    def execute(self, *a, **kw):
        return self._con.execute(*a, **kw)

    def executescript(self, *a, **kw):
        return self._con.executescript(*a, **kw)

    def commit(self) -> None:
        self._con.commit()

    def rollback(self) -> None:
        self._con.rollback()

    def close(self) -> None:
        with self._slot:
            for con in self._alle:
                try:
                    con.close()
                except sqlite3.Error:
                    pass
            self._alle = []
        self._lokaal = threading.local()


def verbind(pad: Path) -> Verbinding:
    """Open de opslag en zorg dat het schema er is."""
    return Verbinding(pad)


@contextmanager
def transactie(con):
    """Commit bij succes, rol terug bij een fout. Nooit half afgeboekt budget."""
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
