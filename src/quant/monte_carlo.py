"""Monte Carlo simulace pro odhad nejlepšího/horšího scénáře."""
from __future__ import annotations

import random
from typing import Any

from src.quant.engine import QuantEngine


class MonteCarlo:
    """Spouští Monte Carlo simulaci nad Quant Enginem.

    Pro každou iteraci vybere náhodné hodnoty vstupních předpokladů
    v uvedených rozmezích a vypočítá ROI. Výsledkem je distribuce možných
    výsledků (best case, worst case, pravděpodobnost kladného ROI).
    """

    def __init__(self, engine: QuantEngine | None = None) -> None:
        self.engine = engine or QuantEngine()

    def simulate(
        self,
        model: dict[str, Any],
        iterations: int = 1000,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Spustí simulaci.

        Očekávané klíče ve modelu:
          - investment_range: [min, max]
          - annual_return_range: [min, max]
          - years: int
          - discount_rate_range: [min, max]
        """
        if seed is not None:
            random.seed(seed)

        if iterations <= 0:
            return {
                "iterations": 0,
                "positive_roi_probability": None,
                "roi_min": None,
                "roi_max": None,
                "roi_median": None,
                "roi_p10": None,
                "roi_p90": None,
                "npv_min": None,
                "npv_max": None,
                "results": [],
                "status": "ok",
            }

        investment_range = model.get("investment_range", [100000, 100000])
        annual_return_range = model.get("annual_return_range", [0, 0])
        years = int(model.get("years", 1))
        discount_rate_range = model.get("discount_rate_range", [0, 0])

        results: list[dict[str, Any]] = []
        positive_roi_count = 0

        for _ in range(iterations):
            investment = random.uniform(*investment_range)
            annual_return = random.uniform(*annual_return_range)
            discount_rate = random.uniform(*discount_rate_range)

            result = self.engine.compute_roi(
                {
                    "investment": investment,
                    "annual_return": annual_return,
                    "years": years,
                    "discount_rate": discount_rate,
                }
            )

            roi = result.get("roi")
            if roi is not None and roi > 0:
                positive_roi_count += 1

            results.append(
                {
                    "investment": round(investment, 2),
                    "annual_return": round(annual_return, 2),
                    "discount_rate": round(discount_rate, 4),
                    "roi": roi,
                    "npv": result.get("npv"),
                    "payback_years": result.get("payback_years"),
                }
            )

        rois = [r["roi"] for r in results if r["roi"] is not None]
        rois.sort()

        def percentile(data: list[float], p: float) -> float | None:
            if not data:
                return None
            k = (len(data) - 1) * (p / 100)
            f = int(k)
            c = f + 1
            if c >= len(data):
                return data[-1]
            d = k - f
            return data[f] + d * (data[c] - data[f])

        return {
            "iterations": iterations,
            "positive_roi_probability": round(
                (positive_roi_count / iterations) * 100, 2
            ),
            "roi_min": round(min(rois), 2) if rois else None,
            "roi_max": round(max(rois), 2) if rois else None,
            "roi_median": round(percentile(rois, 50), 2) if rois else None,
            "roi_p10": round(percentile(rois, 10), 2) if rois else None,
            "roi_p90": round(percentile(rois, 90), 2) if rois else None,
            "npv_min": round(min(r["npv"] for r in results if r["npv"] is not None), 2)
            if any(r["npv"] is not None for r in results)
            else None,
            "npv_max": round(max(r["npv"] for r in results if r["npv"] is not None), 2)
            if any(r["npv"] is not None for r in results)
            else None,
            "results": results,
            "status": "ok",
        }