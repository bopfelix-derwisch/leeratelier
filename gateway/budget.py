"""Dag- en persoonsbudget.

Kernidee uit het plan: rantsoeneer het model, niet de deur. Het lichte pad is
onbeperkt; alleen live modelantwoorden kosten een beurt.

De reset om middernacht is geen taak die moet draaien maar een gevolg van de sleutel:
verbruik wordt geboekt per (bezoeker, datum). Een nieuwe dag is een nieuwe rij, en die
begint op nul. Een gemiste cron kan het budget dus niet vastzetten -- belangrijk voor
een atelier dat onbewaakt draait.

Reserveren gebeurt vooraf per module, zodat niemand halverwege een module zonder
budget valt. Dat is regel 1 van het modulecontract.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .db import transactie


@dataclass
class Stand:
    persoonlijk_resterend: int
    persoonlijk_totaal: int
    dag_resterend: int
    dag_totaal: int
    reset_om: str


class BudgetOp(Exception):
    """Het persoonlijke of het dagbudget is uitgeput."""

    def __init__(self, reset_om: str, welk: str = "persoonlijk"):
        super().__init__(f"budget_op ({welk})")
        self.reset_om = reset_om
        self.welk = welk


class Budget:
    def __init__(self, con: sqlite3.Connection, inst):
        self.con = con
        self.inst = inst
        self.zone = ZoneInfo(inst.reset_tijdzone)

    # -- tijd ---------------------------------------------------------------
    def _nu(self) -> datetime:
        return datetime.now(self.zone)

    def datum(self) -> str:
        return self._nu().strftime("%Y-%m-%d")

    def reset_om(self) -> str:
        morgen = (self._nu() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        return morgen.isoformat()

    # -- lezen --------------------------------------------------------------
    def _rij(self, bezoeker_id: str) -> tuple:
        r = self.con.execute(
            "SELECT beurten, gereserveerd FROM verbruik WHERE bezoeker_id=? AND datum=?",
            (bezoeker_id, self.datum())).fetchone()
        return (r["beurten"], r["gereserveerd"]) if r else (0, 0)

    def dag_verbruikt(self) -> int:
        r = self.con.execute(
            "SELECT COALESCE(SUM(beurten),0) AS n FROM verbruik WHERE datum=?",
            (self.datum(),)).fetchone()
        return int(r["n"])

    def stand(self, bezoeker_id: str) -> Stand:
        beurten, gereserveerd = self._rij(bezoeker_id)
        gebruikt = beurten + gereserveerd
        return Stand(
            persoonlijk_resterend=max(0, self.inst.per_bezoeker - gebruikt),
            persoonlijk_totaal=self.inst.per_bezoeker,
            dag_resterend=max(0, self.dagbudget_voor(bezoeker_id) - self.dag_verbruikt()),
            dag_totaal=self.dagbudget_voor(bezoeker_id),
            reset_om=self.reset_om(),
        )

    def dagbudget_voor(self, bezoeker_id: str) -> int:
        """Het dagbudget dat voor deze bezoeker geldt.

        Op de dag van de begeleide tegenspraaksessie wordt een deel vrijgehouden voor
        de deelnemers. Zonder die reservering kan een drukke ochtend de sessie
        leegtrekken, en die sessie is volgens het plan de enige schakel tussen de route
        en de praktijk -- dus juist het stuk dat je niet wilt verliezen.

        Staat er geen sessiedatum in de config, dan verandert er niets.
        """
        if not self.inst.sessie_datum or self.inst.sessie_datum != self.datum():
            return self.inst.dagbudget
        if bezoeker_id in self.inst.sessie_deelnemers:
            return self.inst.dagbudget
        return int(self.inst.dagbudget * (1.0 - self.inst.gereserveerd_sessie))

    def dag_verbruikt_pct(self) -> int:
        if self.inst.dagbudget <= 0:
            return 100
        return min(100, round(self.dag_verbruikt() / self.inst.dagbudget * 100))

    # -- schrijven ----------------------------------------------------------
    def _zorg_rij(self, bezoeker_id: str) -> None:
        self.con.execute(
            "INSERT OR IGNORE INTO verbruik (bezoeker_id, datum, beurten, gereserveerd) "
            "VALUES (?, ?, 0, 0)", (bezoeker_id, self.datum()))

    def reserveer(self, bezoeker_id: str, aantal: int) -> int:
        """Zet `aantal` beurten opzij. Geeft het gereserveerde aantal terug.

        Reserveren telt mee voor het persoonlijke budget maar nog niet voor het
        dagbudget: pas bij daadwerkelijk verbruik gaat er iets van de dag af. Een
        bezoeker die een module opent en weer weggaat, kost het atelier niets.
        """
        if aantal <= 0:
            return 0
        with transactie(self.con):
            self._zorg_rij(bezoeker_id)
            # De klemmende voorwaarde staat in de UPDATE zelf, niet in Python.
            # Acht gelijktijdige verzoeken lezen anders allemaal dezelfde stand
            # voordat een van hen schrijft, en het budget loopt over.
            self.con.execute(
                "UPDATE verbruik SET gereserveerd = gereserveerd + "
                "  MIN(?, MAX(0, ? - beurten - gereserveerd)) "
                "WHERE bezoeker_id=? AND datum=?",
                (aantal, self.inst.per_bezoeker, bezoeker_id, self.datum()))
            beurten, gereserveerd = self._rij(bezoeker_id)
        if beurten + gereserveerd >= self.inst.per_bezoeker and gereserveerd == 0:
            raise BudgetOp(self.reset_om(), "persoonlijk")
        return min(aantal, max(0, self.inst.per_bezoeker - beurten))

    def reserveer_minstens(self, bezoeker_id: str, aantal: int) -> int:
        """Zorg dat er *minstens* `aantal` beurten opzij staan. Idempotent.

        Dit is wat het openen van een module nodig heeft. `reserveer` telt op, en dat
        is fout bij herhaald openen: wie een modulepagina twintig keer ververst, zou
        anders zijn hele budget in reserveringen kwijt zijn zonder een vraag te stellen.
        Waargenomen bij de doorloop van WP-06.
        """
        if aantal <= 0:
            return 0
        with transactie(self.con):
            self._zorg_rij(bezoeker_id)
            self.con.execute(
                "UPDATE verbruik SET gereserveerd = MAX(gereserveerd, "
                "  MIN(?, MAX(0, ? - beurten))) "
                "WHERE bezoeker_id=? AND datum=?",
                (aantal, self.inst.per_bezoeker, bezoeker_id, self.datum()))
            _, gereserveerd = self._rij(bezoeker_id)
        return gereserveerd

    def controleer(self, bezoeker_id: str) -> None:
        """Kan deze bezoeker nu één beurt verbruiken? Zo nee: BudgetOp.

        Alleen `beurten` telt hier, niet `gereserveerd`. Een reservering heeft bij
        het aanmaken al ruimte binnen het persoonlijke budget opgeëist; er nu nog
        eens tegen toetsen zou dezelfde beurt twee keer aanrekenen en een bezoeker
        halverwege een gereserveerde module laten stranden.
        """
        beurten, _ = self._rij(bezoeker_id)
        if beurten >= self.inst.per_bezoeker:
            raise BudgetOp(self.reset_om(), "persoonlijk")
        if self.dag_verbruikt() >= self.dagbudget_voor(bezoeker_id):
            raise BudgetOp(self.reset_om(), "dag")

    def reservering(self, bezoeker_id: str) -> int:
        """Hoeveel beurten staan er voor deze bezoeker opzij?

        Het portaal reserveert bij het openen van een module het aantal uit de
        frontmatter. Een vraag binnen die module put daaruit en reserveert niet
        nog eens -- anders wordt dezelfde beurt twee keer van het budget gehaald.
        """
        _, gereserveerd = self._rij(bezoeker_id)
        return gereserveerd

    def boek_af(self, bezoeker_id: str, aantal: int = 1) -> None:
        """Verbruik beurten. Neemt eerst van de reservering, dan van de ruimte.

        In één UPDATE, zodat twee gelijktijdige werkers elkaars afboeking niet
        overschrijven.
        """
        with transactie(self.con):
            self._zorg_rij(bezoeker_id)
            self.con.execute(
                "UPDATE verbruik SET beurten = beurten + ?, "
                "  gereserveerd = MAX(0, gereserveerd - ?) "
                "WHERE bezoeker_id=? AND datum=?",
                (aantal, aantal, bezoeker_id, self.datum()))

    def geef_terug(self, bezoeker_id: str, aantal: int = 1) -> None:
        """Reservering vrijgeven zonder te verbruiken.

        Nodig bij een antwoord uit cache of conserven: dat kost geen modelbeurt, en
        het zou oneerlijk zijn de bezoeker ervoor te laten betalen.
        """
        if aantal <= 0:
            return
        with transactie(self.con):
            self.con.execute(
                "UPDATE verbruik SET gereserveerd = MAX(0, gereserveerd - ?) "
                "WHERE bezoeker_id=? AND datum=?", (aantal, bezoeker_id, self.datum()))
