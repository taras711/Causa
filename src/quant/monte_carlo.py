"""Monte Carlo simulace pro odhad nejlepšího/horšího scénáře."""
from __future__ import annotations

import math
import random
from typing import Any

from src.quant.engine import QuantEngine, _safe_float


class MonteCarlo:
    """Spouští Monte Carlo simulaci nad Quant Enginem."""

    MAX_ITERATIONS = 100_000

    def __init__(self, engine: QuantEngine | None = None) -> None:
        self.engine = engine or QuantEngine()

    def _safe_range(self, value: Any, default: tuple[float, float]) -> tuple[float, float]:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            return default
        a = _safe_float(value[0])
        b = _safe_float(value[1])
        if a is None or b is None:
            return default
        lo, hi = (a, b) if a <= b else (b, a)
        return lo, hi

    def simulate(
        self,
        model: dict[str, Any],
        iterations: int = 1000,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Spustí simulaci."""
        if not isinstance(model, dict):
            model = {}

        try:
            iterations = int(iterations)
        except (TypeError, ValueError):
            iterations = 0

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

        if iterations > self.MAX_ITERATIONS:
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
                "status": "error: too many iterations",
            }

        if seed is not None:
            try:
                random.seed(int(seed))
            except (TypeError, ValueError):
                random.seed()

        investment_range = self._safe_range(
            model.get("investment_range", [100000, 100000]), (100000.0, 100000.0)
        )
        annual_return_range = self._safe_range(
            model.get("annual_return_range", [0, 0]), (0.0, 0.0)
        )
        discount_rate_range = self._safe_range(
            model.get("discount_rate_range", [0, 0]), (0.0, 0.0)
        )

        raw_years = model.get("years", 1)
        try:
            years = int(raw_years)
        except (TypeError, ValueError):
            years = 1
        if years < 0 or years > self.engine.MAX_YEARS:
            years = 1

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

        npvs = [r["npv"] for r in results if r["npv"] is not None]

        positive_prob = None
        if iterations > 0:
            positive_prob = round((positive_roi_count / iterations) * 100, 2)

        return {
            "iterations": iterations,
            "positive_roi_probability": positive_prob,
            "roi_min": round(min(rois), 2) if rois else None,
            "roi_max": round(max(rois), 2) if rois else None,
            "roi_median": round(percentile(rois, 50), 2) if rois else None,
            "roi_p10": round(percentile(rois, 10), 2) if rois else None,
            "roi_p90": round(percentile(rois, 90), 2) if rois else None,
            "npv_min": round(min(npvs), 2) if npvs else None,
            "npv_max": round(max(npvs), 2) if npvs else None,
            "results": results,
            "status": "ok",
        }
