"""Deterministický Quant Engine – ROI, citlivost, Monte Carlo.

Pravidlo: LLM nikdy nevyrábí čísla. Všechny výpočty jsou deterministické
a plně auditovatelné. Vstupy pocházejí z dat klienta nebo explicitně
označených předpokladů (Assumption).
"""
from __future__ import annotations

import math
from typing import Any


def _safe_float(value: Any) -> float | None:
    """Bezpečně převede hodnotu na float; vrací None při neplatné/nefiniální hodnotě."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


class QuantEngine:
    """Hlavní vstup do Quant Enginu. Deleguje na specializované výpočty."""

    MAX_YEARS = 10_000

    def compute_roi(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Vypočítá návratnost investice (ROI)."""
        if not isinstance(inputs, dict):
            inputs = {}

        investment = _safe_float(inputs.get("investment", 0))
        annual_return = _safe_float(inputs.get("annual_return", 0))
        discount_rate = _safe_float(inputs.get("discount_rate", 0))

        raw_years = inputs.get("years", 1)
        try:
            years = int(raw_years)
        except (TypeError, ValueError):
            return {
                "roi": None,
                "npv": None,
                "payback_years": None,
                "cash_flow": [],
                "status": "error: invalid input",
            }

        if investment is None or annual_return is None or discount_rate is None:
            return {
                "roi": None,
                "npv": None,
                "payback_years": None,
                "cash_flow": [],
                "status": "error: invalid input",
            }

        if years < 0 or years > self.MAX_YEARS:
            return {
                "roi": None,
                "npv": None,
                "payback_years": None,
                "cash_flow": [],
                "status": "error: invalid years",
            }

        if investment <= 0:
            return {
                "roi": None,
                "npv": None,
                "payback_years": None,
                "cash_flow": [],
                "status": "error: investment must be > 0",
            }

        if discount_rate <= -1.0:
            return {
                "roi": None,
                "npv": None,
                "payback_years": None,
                "cash_flow": [],
                "status": "error: discount_rate must be > -1",
            }

        cash_flow = []
        cumulative = -investment
        npv = -investment
        payback_years = None

        denominator_base = 1 + discount_rate

        for year in range(1, years + 1):
            net_cash = annual_return
            cumulative += net_cash
            discount_factor = denominator_base ** year
            contribution = net_cash / discount_factor if discount_factor != 0 else 0.0
            npv += contribution
            cash_flow.append(
                {
                    "year": year,
                    "cash_flow": net_cash,
                    "cumulative": cumulative,
                    "npv_contribution": contribution,
                }
            )
            if payback_years is None and cumulative >= 0:
                payback_years = year

        roi = (cumulative / investment) * 100 if investment > 0 else 0

        return {
            "investment": investment,
            "annual_return": annual_return,
            "years": years,
            "discount_rate": discount_rate,
            "roi": round(roi, 2),
            "npv": round(npv, 2),
            "payback_years": payback_years,
            "total_return": round(cumulative, 2),
            "cash_flow": cash_flow,
            "status": "ok",
        }

    def sensitivity(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Citlivostní analýza."""
        if not isinstance(inputs, dict):
            inputs = {}

        base_case = inputs.get("base_case", {})
        if not isinstance(base_case, dict):
            base_case = {}

        variations = inputs.get("variations", [])
        if not isinstance(variations, list):
            variations = []

        base_result = self.compute_roi(base_case)
        results = []

        for variation in variations:
            if not isinstance(variation, dict):
                continue
            name = variation.get("name", "unknown")
            changes = variation.get("changes", {})
            if not isinstance(changes, dict):
                changes = {}
            modified = dict(base_case)
            for key, value in changes.items():
                modified[key] = value
            varied_result = self.compute_roi(modified)

            roi_delta = None
            if (
                base_result.get("roi") is not None
                and varied_result.get("roi") is not None
            ):
                roi_delta = round(varied_result["roi"] - base_result["roi"], 2)

            results.append(
                {
                    "variation": name,
                    "changes": changes,
                    "roi": varied_result.get("roi"),
                    "npv": varied_result.get("npv"),
                    "roi_delta": roi_delta,
                    "payback_years": varied_result.get("payback_years"),
                }
            )

        return {
            "base_roi": base_result.get("roi"),
            "base_npv": base_result.get("npv"),
            "results": results,
            "status": "ok",
        }
