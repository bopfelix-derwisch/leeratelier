"""Het modulecontract, in code.

`spec/04-modulecontract.md` beschrijft welke velden een module moet hebben en welke
regels erbij horen. Hier worden die regels afgedwongen, en met opzet streng: een
module die niet aan het contract voldoet, rendert niet.

Regel 2 uit het contract is de scherpste: `wat_ging_mis: true` verplicht de sectie
"Wat hier misging". Ontbreekt die, dan faalt het renderen met een duidelijke fout in
plaats van stil door te gaan. Dat is bewust. Fouten uit dit lab zijn het waardevolste
materiaal dat er is, en ze moeten niet wegvallen omdat iemand haastig een module
schreef.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

VERPLICHT = ("id", "titel", "spoor", "volgorde", "competenties", "duur_min",
             "beurten", "modellen", "status", "wat_ging_mis", "bewijs")

SPOREN = ("basis", "waterlab", "leefomgeving", "sturing")
STATUSSEN = ("concept", "gepubliceerd")

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
# "## Wat hier misging", met of zonder kopniveau-variatie.
_MISGING = re.compile(r"^#{1,4}\s*Wat hier misging\s*$", re.M | re.I)


class ModuleFout(Exception):
    """De module voldoet niet aan het contract. Met opzet hard."""


@dataclass
class Module:
    id: str
    titel: str
    spoor: str
    volgorde: int
    competenties: list
    duur_min: int
    beurten: int
    modellen: list
    status: str
    wat_ging_mis: bool
    bewijs: str
    tekst: str                       # de markdown ná de frontmatter
    map: Path
    conserven: str = ""
    poc: str = ""
    routes: list = field(default_factory=list)

    @property
    def gepubliceerd(self) -> bool:
        return self.status == "gepubliceerd"

    @property
    def kost_beurten(self) -> bool:
        return self.beurten > 0

    @property
    def heeft_opdracht(self) -> bool:
        return (self.map / "opdracht.md").exists()


def lees(map_: Path) -> Module:
    """Lees en valideer één module. Gooit ModuleFout bij elke contractbreuk."""
    map_ = Path(map_)
    pad = map_ / "module.md"
    if not pad.exists():
        raise ModuleFout(f"{map_.name}: module.md ontbreekt")

    ruw = pad.read_text(encoding="utf-8")
    m = _FRONTMATTER.match(ruw)
    if not m:
        raise ModuleFout(f"{map_.name}: geen frontmatter")

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as fout:
        raise ModuleFout(f"{map_.name}: frontmatter is geen geldige yaml: {fout}") from fout

    ontbreekt = [v for v in VERPLICHT if v not in fm]
    if ontbreekt:
        raise ModuleFout(f"{map_.name}: frontmatter mist {', '.join(ontbreekt)}")

    if fm["id"] != map_.name:
        raise ModuleFout(f"{map_.name}: id '{fm['id']}' wijkt af van de mapnaam")
    if fm["spoor"] not in SPOREN:
        raise ModuleFout(f"{map_.name}: spoor '{fm['spoor']}' is geen van {SPOREN}")
    if fm["status"] not in STATUSSEN:
        raise ModuleFout(f"{map_.name}: status '{fm['status']}' is geen van {STATUSSEN}")

    tekst = m.group(2)

    # Regel 2 van het contract. Alleen afdwingen bij gepubliceerde modules: een
    # concept mag nog onaf zijn, maar mag dan ook niemand bereiken.
    if fm["wat_ging_mis"] and fm["status"] == "gepubliceerd" and not _MISGING.search(tekst):
        raise ModuleFout(
            f"{map_.name}: wat_ging_mis staat op true maar de sectie "
            f"'Wat hier misging' ontbreekt. Zie spec/04-modulecontract.md regel 2.")

    return Module(
        id=fm["id"], titel=fm["titel"], spoor=fm["spoor"], volgorde=int(fm["volgorde"]),
        competenties=list(fm["competenties"] or []), duur_min=int(fm["duur_min"]),
        beurten=int(fm["beurten"]), modellen=list(fm["modellen"] or []),
        status=fm["status"], wat_ging_mis=bool(fm["wat_ging_mis"]), bewijs=fm["bewijs"],
        conserven=fm.get("conserven") or "", poc=fm.get("poc") or "",
        routes=list(fm.get("routes") or []), tekst=tekst, map=map_,
    )


def lees_alle(modules_dir: Path) -> tuple:
    """Alle modules, plus de fouten. Eén kapotte module sloopt de route niet.

    Nette degradatie boven harde aannames: het portaal blijft staan en de
    facilitator ziet welke module stuk is.
    """
    modules, fouten = [], []
    modules_dir = Path(modules_dir)
    if not modules_dir.is_dir():
        return [], []
    for map_ in sorted(p for p in modules_dir.iterdir() if p.is_dir()):
        try:
            modules.append(lees(map_))
        except ModuleFout as fout:
            fouten.append(str(fout))
    modules.sort(key=lambda m: (m.spoor != "basis", m.volgorde))
    return modules, fouten
