"""Configuratie voor de leerbemiddelaar.

Budgetwaarden staan in `config/budget.yaml` en modelgegevens in `config/modellen.yaml`.
Ze worden hier eenmaal gelezen en verder als gewone objecten doorgegeven, zodat geen
enkele module zelf een bestand hoeft te openen -- en zodat een test een andere
configuratie kan meegeven zonder de schijf aan te raken.

`CLAUDE.md`: geen budgetwaarden hardcoderen. Dat geldt ook voor "even snel" een
standaardwaarde in een functie zetten; alles komt hier vandaan.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

WORTEL = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Instellingen:
    dagbudget: int
    per_bezoeker: int
    gereserveerd_sessie: float
    gelijktijdig: dict          # {"klasmodel": 4, "showmodel": 2}
    sessie_datum: str           # "" als er geen sessie gepland is
    sessie_deelnemers: tuple
    reset_tijdzone: str
    cache_aan: bool
    cache_uren: int
    logboek_aan: bool
    logboek_dagen: int
    modellen: dict              # {"klas": {...}, "show": {...}}
    db_pad: Path
    conserven_dir: Path
    modules_dir: Path
    rag_dir: Path
    # Gemeten mediaan per model; voedt de wachttijdschatting tot er echte
    # metingen binnen zijn. Uit ops/ijking/, niet verzonnen.
    mediaan_s: dict = field(default_factory=lambda: {"klas": 5.5, "show": 24.1})


def _pad(waarde: str, standaard: Path) -> Path:
    return Path(waarde) if waarde else standaard


def laad(wortel: Path = WORTEL) -> Instellingen:
    budget = yaml.safe_load((wortel / "config" / "budget.yaml").read_text(encoding="utf-8"))
    modellen = yaml.safe_load((wortel / "config" / "modellen.yaml").read_text(encoding="utf-8"))

    klas, show = modellen.get("klasmodel") or {}, modellen.get("showmodel") or {}
    return Instellingen(
        dagbudget=int(budget["dagbudget_modelbeurten"]),
        per_bezoeker=int(budget["per_bezoeker_per_dag"]),
        gereserveerd_sessie=float(budget.get("gereserveerd_begeleide_sessie", 0.0)),
        gelijktijdig={
            "klas": int(budget["gelijktijdig"]["klasmodel"]),
            "show": int(budget["gelijktijdig"]["showmodel"]),
        },
        sessie_datum=str((budget.get("begeleide_sessie") or {}).get("datum") or ""),
        sessie_deelnemers=tuple(
            (budget.get("begeleide_sessie") or {}).get("deelnemers") or ()),
        reset_tijdzone=str(budget["reset"]["tijdzone"]),
        cache_aan=bool(budget["cache"]["inschakelen"]),
        cache_uren=int(budget["cache"]["bewaartermijn_uren"]),
        logboek_aan=bool(budget["logboek"]["inschakelen"]),
        logboek_dagen=int(budget["logboek"]["bewaartermijn_dagen"]),
        modellen={
            "klas": {
                "naam": klas.get("naam") or "onbekend",
                "endpoint": f"http://127.0.0.1:{klas.get('poort', 8081)}",
            },
            "show": {
                "naam": show.get("naam") or "onbekend",
                "endpoint": f"http://127.0.0.1:{show.get('poort', 8080)}",
            },
            "embed": {
                "naam": (modellen.get("embeddings") or {}).get("naam") or "bge-m3",
                "endpoint": f"http://127.0.0.1:{(modellen.get('embeddings') or {}).get('poort', 8082)}",
            },
        },
        db_pad=_pad(os.environ.get("ATELIER_DB", ""), Path("/mnt/nvme/leeratelier/atelier.db")),
        conserven_dir=wortel / "content" / "conserven",
        modules_dir=wortel / "content" / "modules",
        rag_dir=Path("/mnt/nvme/geluidsmeter/data/rag"),
    )
