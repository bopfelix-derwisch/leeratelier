"""Markdown naar HTML, en de bemiddelaar-client.

Het portaal rendert modules uit markdown en praat verder alleen met de bemiddelaar
op :8794. Het kent geen modellen, geen budgetdatabase en geen conserven: die zitten
allemaal achter dat ene contract. Dat is met opzet -- het portaal is een gezicht,
geen tweede plek waar beleid staat.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import jinja2
import markdown as md
from fastapi.responses import HTMLResponse

# Geen extensies die HTML uit de bron doorlaten. Modules zijn door de facilitator
# geschreven en dus vertrouwd, maar er is geen reden ruimte te laten die niemand
# nodig heeft.
_MD = md.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"],
                  output_format="html5")


def naar_html(tekst: str) -> str:
    _MD.reset()
    return _MD.convert(tekst or "")


class Sjablonen:
    """Jinja2 rechtstreeks, zonder de wrapper van Starlette.

    Starlette 1.2 verwacht Jinja2 3.1 of nieuwer; op deze machine staat 3.0.3 als
    systeempakket. Dat opwaarderen raakt elke andere dienst op orin3, en dat is een
    zware ingreep voor een sjabloonlaag van tien regels. Rechtstreeks werken haalt
    de koppeling helemaal weg.
    """

    def __init__(self, map_: Path):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(map_)),
            autoescape=jinja2.select_autoescape(["html"]),
            trim_blocks=True, lstrip_blocks=True)

    def html(self, naam: str, context: dict, status_code: int = 200) -> HTMLResponse:
        return HTMLResponse(self.env.get_template(naam).render(**context),
                            status_code=status_code)


class Bemiddelaar:
    """Client voor :8794. Elke fout wordt een lege of veilige waarde.

    Het portaal moet blijven staan als de bemiddelaar wegvalt: een bezoeker die
    een modulepagina opent, hoort de tekst gewoon te zien. Alleen het vragen zelf
    werkt dan niet, en dat vertelt de storingsbanner.
    """

    def __init__(self, basis: str, timeout_s: float = 10.0):
        self.basis = basis.rstrip("/")
        self.timeout_s = timeout_s

    async def _get(self, pad: str, standaard):
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as c:
                r = await c.get(self.basis + pad)
                r.raise_for_status()
                return r.json()
        except (httpx.HTTPError, ValueError):
            return standaard

    async def _post(self, pad: str, data: dict):
        async with httpx.AsyncClient(timeout=self.timeout_s) as c:
            r = await c.post(self.basis + pad, json=data)
            return r.status_code, (r.json() if r.content else {})

    async def gezondheid(self) -> dict:
        return await self._get("/v1/gezondheid", {
            "klasmodel": "onbekend", "showmodel": "onbekend", "embeddings": "onbekend",
            "wachtrij_diepte": 0, "dagbudget_verbruikt_pct": 0,
            "rag_index_leeftijd_dagen": None, "storingsmodus": True,
            "open_meldingen": 0, "conserven": 0, "bemiddelaar": "weg"})

    async def budget(self, bezoeker_id: str) -> dict:
        return await self._get(f"/v1/budget/{bezoeker_id}", {
            "persoonlijk_resterend": 0, "persoonlijk_totaal": 0,
            "dag_resterend": 0, "dag_totaal": 0, "reset_om": ""})

    async def taak(self, taak_id: str):
        return await self._get(f"/v1/taak/{taak_id}", None)

    async def vraag(self, bezoeker_id: str, module_id: str, tekst: str,
                    model_voorkeur: str = "auto"):
        return await self._post("/v1/vraag", {
            "bezoeker_id": bezoeker_id, "module_id": module_id,
            "vraag": tekst, "model_voorkeur": model_voorkeur})

    async def reserveer(self, bezoeker_id: str, module_id: str, beurten: int):
        return await self._post("/v1/reserveer", {
            "bezoeker_id": bezoeker_id, "module_id": module_id, "beurten": beurten})

    async def melding(self, bezoeker_id: str, module_id: str, tekst: str, context: dict):
        return await self._post("/v1/melding", {
            "bezoeker_id": bezoeker_id, "module_id": module_id,
            "tekst": tekst, "context": context})
