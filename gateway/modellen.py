"""Praten met de llama.cpp-servers, en weten of ze er zijn.

Twee modellen: het klasmodel op :8081 (standaard voor alle bezoekersvragen) en het
showmodel op :8080 (demonstratie en vergelijking, traag en gerantsoeneerd). Plus de
embeddings op :8082, waar de bemiddelaar zelf niets mee doet maar de gezondheid wel
over rapporteert.

Gemeten in WP-01 en WP-04: het klasmodel haalt 24 tok/s en een p50 van 5,5 s, het
showmodel 6,2 tok/s en een p50 van 16 s. Vandaar de ruime timeout -- een showmodel
dat 90 seconden doet over een lang antwoord is traag, niet stuk.
"""

from __future__ import annotations

import time

import httpx

SYSTEEM = (
    "Je bent een assistent in een leeratelier voor Nederlandse functioneel beheerders. "
    "Antwoord in het Nederlands, bondig, en zeg het als je iets niet zeker weet."
)


class ModelWeg(Exception):
    """Het model antwoordt niet. De ladder valt een trede verder."""


async def leeft(endpoint: str, timeout_s: float = 3.0) -> bool:
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as c:
            r = await c.get(f"{endpoint.rstrip('/')}/health")
            return r.status_code == 200
    except httpx.HTTPError:
        return False


async def vraag(endpoint: str, tekst: str, max_tokens: int = 400,
                timeout_s: float = 180.0) -> tuple:
    """Stel één vraag. Geeft (antwoord, latency_ms) terug of gooit ModelWeg."""
    payload = {
        "model": "local",
        "messages": [{"role": "system", "content": SYSTEEM},
                     {"role": "user", "content": tekst}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as c:
            r = await c.post(f"{endpoint.rstrip('/')}/v1/chat/completions", json=payload)
            r.raise_for_status()
            body = r.json()
    except (httpx.HTTPError, ValueError) as fout:
        raise ModelWeg(str(fout)) from fout

    latency_ms = int((time.perf_counter() - start) * 1000)
    keuzes = body.get("choices") or []
    antwoord = (keuzes[0].get("message", {}).get("content") or "").strip() if keuzes else ""
    if not antwoord:
        raise ModelWeg("leeg antwoord")
    return antwoord, latency_ms


async def vraag_poc(endpoint: str, tekst: str, timeout_s: float = 180.0) -> tuple:
    """Stel de vraag aan een POC met een eigen zoekindex.

    Het verschil met `vraag` is de ophaalstap. Dezelfde vraag levert via het kale
    model iets over beleggingsrisico op en via de POC het juiste wetsartikel -- want
    daar zit een index tussen. Modules die over RAG gaan, moeten hierlangs.

    Geeft (antwoord, latency_ms, bronnen, contract) terug of gooit ModelWeg. Het
    contract -- disclaimer, vangnet, onzekerheid -- gaat mee omdat module L3 er
    letterlijk over gaat: je kunt pas zien dat `onzekerheid` altijd op waar staat
    als je het veld te zien krijgt.
    """
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as c:
            r = await c.post(endpoint, json={"vraag": tekst})
            r.raise_for_status()
            body = r.json()
    except (httpx.HTTPError, ValueError) as fout:
        raise ModelWeg(str(fout)) from fout

    antwoord = (body.get("antwoord") or "").strip()
    if not antwoord:
        raise ModelWeg("poc gaf geen antwoord")
    bronnen = []
    for b in (body.get("bronnen") or []):
        bronnen.append(b.get("url") if isinstance(b, dict) else str(b))
    contract = {k: body[k] for k in ("onzekerheid", "disclaimer", "vangnet")
                if k in body}
    return antwoord, int((time.perf_counter() - start) * 1000), bronnen, contract
