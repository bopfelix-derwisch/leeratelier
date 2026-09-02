#!/usr/bin/env python3
"""IJkmeting voor WP-01: wat kan deze machine werkelijk aan?

Meet latency, doorzet en tijd-tot-eerste-token van een llama-server bij oplopende
gelijktijdigheid. Alleen stdlib, zodat dit op orin3 draait zonder installatie.

    python3 meet.py --endpoint http://127.0.0.1:8080 --concurrency 1 2 4 --n 6 \
        --out rapport-2026-09-02.json

Het resultaat vult config/budget.yaml. Draai dit voordat je een dagbudget vastlegt.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

STANDAARD_PROMPT = (
    "Leg in vier zinnen uit wat een omgevingsvergunning is en wanneer je er een nodig hebt."
)


def geheugen_mb() -> dict[str, int]:
    """Vrij en gebruikt geheugen in MB. Valt stil terug als free ontbreekt."""
    try:
        uit = subprocess.run(
            ["free", "-m"], capture_output=True, text=True, timeout=5, check=True
        ).stdout.splitlines()
        velden = uit[1].split()
        return {"totaal": int(velden[1]), "gebruikt": int(velden[2]), "vrij": int(velden[3])}
    except Exception:
        return {}


class Tegrastats:
    """Bemonstert RAM en GPU-bezetting met tegrastats zolang een meting loopt.

    `free -m` ziet het unified memory maar niet de GPU-bezetting, en juist die laat zien
    of de machine daadwerkelijk aan het werk is of staat te wachten. Valt stil terug als
    tegrastats ontbreekt of niet mag draaien; de meting gaat dan gewoon door.
    """

    PATROON_RAM = re.compile(r"RAM (\d+)/(\d+)MB")
    PATROON_GPU = re.compile(r"GR3D_FREQ (\d+)%")

    def __init__(self, interval_ms: int = 1000) -> None:
        self.interval_ms = interval_ms
        self.proces: subprocess.Popen | None = None
        self.monsters: list[tuple[int, int]] = []   # (ram_mb, gpu_pct)
        self._draad: threading.Thread | None = None

    def start(self) -> None:
        try:
            self.proces = subprocess.Popen(
                ["tegrastats", "--interval", str(self.interval_ms)],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            )
        except (FileNotFoundError, PermissionError):
            self.proces = None
            return
        self._draad = threading.Thread(target=self._lees, daemon=True)
        self._draad.start()

    def _lees(self) -> None:
        assert self.proces and self.proces.stdout
        for regel in self.proces.stdout:
            ram = self.PATROON_RAM.search(regel)
            gpu = self.PATROON_GPU.search(regel)
            if ram:
                self.monsters.append((int(ram.group(1)), int(gpu.group(1)) if gpu else -1))

    def markeer(self) -> int:
        """Huidig aantal monsters, als startpunt voor `sinds`."""
        return len(self.monsters)

    def sinds(self, mark: int) -> dict:
        venster = self.monsters[mark:]
        if not venster:
            return {}
        ram = [m[0] for m in venster]
        gpu = [m[1] for m in venster if m[1] >= 0]
        uit = {"monsters": len(venster), "ram_piek_mb": max(ram),
               "ram_gemiddeld_mb": int(statistics.mean(ram))}
        if gpu:
            uit |= {"gpu_piek_pct": max(gpu), "gpu_gemiddeld_pct": int(statistics.mean(gpu))}
        return uit

    def stop(self) -> None:
        if self.proces:
            self.proces.terminate()
            try:
                self.proces.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proces.kill()


def een_verzoek(endpoint: str, prompt: str, max_tokens: int, timeout: int) -> dict:
    """Eén completion. Meet totale duur en, bij streaming, tijd tot eerste token."""
    payload = json.dumps(
        {
            "model": "local",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "stream": True,
            "temperature": 0.2,
        }
    ).encode()

    verzoek = urllib.request.Request(
        f"{endpoint.rstrip('/')}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    start = time.perf_counter()
    eerste_token: float | None = None
    tokens = 0

    try:
        with urllib.request.urlopen(verzoek, timeout=timeout) as resp:
            for regel in resp:
                regel = regel.decode("utf-8", "replace").strip()
                if not regel.startswith("data:"):
                    continue
                body = regel[5:].strip()
                if body == "[DONE]":
                    break
                try:
                    brok = json.loads(body)
                except json.JSONDecodeError:
                    continue
                delta = brok.get("choices", [{}])[0].get("delta", {}).get("content")
                if delta:
                    if eerste_token is None:
                        eerste_token = time.perf_counter() - start
                    tokens += 1
    except (urllib.error.URLError, TimeoutError, OSError) as fout:
        return {"ok": False, "fout": str(fout), "duur_s": time.perf_counter() - start}

    duur = time.perf_counter() - start
    return {
        "ok": True,
        "duur_s": round(duur, 3),
        "ttft_s": round(eerste_token, 3) if eerste_token else None,
        "tokens": tokens,
        "tok_per_s": round(tokens / duur, 2) if duur > 0 else None,
    }


def meet_niveau(endpoint: str, gelijktijdig: int, n: int, prompt: str,
                max_tokens: int, timeout: int, tegra: "Tegrastats | None" = None) -> dict:
    print(f"  gelijktijdigheid {gelijktijdig}: {n} verzoeken...", flush=True)
    voor = geheugen_mb()
    mark = tegra.markeer() if tegra else 0
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=gelijktijdig) as pool:
        resultaten = list(
            pool.map(lambda _: een_verzoek(endpoint, prompt, max_tokens, timeout), range(n))
        )

    wandkloktijd = time.perf_counter() - start
    na = geheugen_mb()
    geslaagd = [r for r in resultaten if r.get("ok")]
    duren = sorted(r["duur_s"] for r in geslaagd)

    def perc(p: float) -> float | None:
        if not duren:
            return None
        return round(duren[min(len(duren) - 1, int(len(duren) * p))], 2)

    return {
        "gelijktijdig": gelijktijdig,
        "verzoeken": n,
        "geslaagd": len(geslaagd),
        "mislukt": n - len(geslaagd),
        "p50_s": perc(0.5),
        "p95_s": perc(0.95),
        "gemiddeld_s": round(statistics.mean(duren), 2) if duren else None,
        "ttft_mediaan_s": round(
            statistics.median([r["ttft_s"] for r in geslaagd if r.get("ttft_s")]), 2
        ) if any(r.get("ttft_s") for r in geslaagd) else None,
        "tok_per_s_mediaan": round(
            statistics.median([r["tok_per_s"] for r in geslaagd if r.get("tok_per_s")]), 2
        ) if any(r.get("tok_per_s") for r in geslaagd) else None,
        "doorzet_per_min": round(len(geslaagd) / wandkloktijd * 60, 1) if wandkloktijd else None,
        "geheugen_voor_mb": voor,
        "geheugen_na_mb": na,
        "tegrastats": tegra.sinds(mark) if tegra else {},
        "fouten": [r.get("fout") for r in resultaten if not r.get("ok")][:3],
    }


def dagbudget(metingen: list[dict], venster_uur: float, belasting: float) -> dict:
    """Leid een dagbudget af uit de beste gemeten doorzet."""
    doorzetten = [m["doorzet_per_min"] for m in metingen if m.get("doorzet_per_min")]
    if not doorzetten:
        return {"opmerking": "geen geslaagde metingen"}
    beste = max(doorzetten)
    theoretisch = beste * 60 * venster_uur
    return {
        "beste_doorzet_per_min": beste,
        "venster_uur": venster_uur,
        "aangenomen_belasting": belasting,
        "theoretisch_per_dag": int(theoretisch),
        "advies_dagbudget_beurten": int(theoretisch * belasting),
        "toelichting": (
            "Zet dit in config/budget.yaml. Begin lager dan het advies: een atelier dat rustig "
            "aanvoelt is meer waard dan een atelier dat precies vol zit."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="IJkmeting llama-server")
    p.add_argument("--endpoint", default="http://127.0.0.1:8080")
    p.add_argument("--concurrency", type=int, nargs="+", default=[1, 2, 4])
    p.add_argument("--n", type=int, default=6, help="verzoeken per niveau")
    p.add_argument("--max-tokens", type=int, default=200)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--prompt", default=STANDAARD_PROMPT)
    p.add_argument("--venster-uur", type=float, default=24.0,
                   help="het atelier is permanent open; 24 is de standaard")
    p.add_argument("--belasting", type=float, default=0.40,
                   help="aandeel van de capaciteit dat je durft te vullen")
    p.add_argument("--geen-tegrastats", action="store_true",
                   help="alleen free -m; tegrastats overslaan")
    p.add_argument("--out", default=None)
    a = p.parse_args()

    print(f"IJkmeting tegen {a.endpoint}")
    print(f"Geheugen vooraf: {geheugen_mb()}\n")

    tegra = None
    if not a.geen_tegrastats:
        tegra = Tegrastats()
        tegra.start()
        if tegra.proces is None:
            print("  (tegrastats niet beschikbaar; alleen free -m)\n", flush=True)
            tegra = None

    try:
        metingen = [
            meet_niveau(a.endpoint, c, a.n, a.prompt, a.max_tokens, a.timeout, tegra)
            for c in a.concurrency
        ]
    finally:
        if tegra:
            tegra.stop()

    rapport = {
        "tijdstip": datetime.now().isoformat(timespec="seconds"),
        "endpoint": a.endpoint,
        "prompt": a.prompt,
        "max_tokens": a.max_tokens,
        "metingen": metingen,
        "afgeleid_budget": dagbudget(metingen, a.venster_uur, a.belasting),
    }

    print("\n" + "-" * 66)
    print(f"{'gelijktijdig':>13} {'p50':>8} {'p95':>8} {'ttft':>8} {'tok/s':>8} "
          f"{'per min':>9} {'gpu%':>6} {'ram MB':>8}")
    for m in metingen:
        tg = m.get("tegrastats") or {}
        print(
            f"{m['gelijktijdig']:>13} {str(m['p50_s']):>8} {str(m['p95_s']):>8} "
            f"{str(m['ttft_mediaan_s']):>8} {str(m['tok_per_s_mediaan']):>8} "
            f"{str(m['doorzet_per_min']):>9} {str(tg.get('gpu_gemiddeld_pct','-')):>6} "
            f"{str(tg.get('ram_piek_mb','-')):>8}"
        )
    print("-" * 66)
    print(json.dumps(rapport["afgeleid_budget"], indent=2, ensure_ascii=False))

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rapport, f, indent=2, ensure_ascii=False)
        print(f"\nRapport geschreven naar {a.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
