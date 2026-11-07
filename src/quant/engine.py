"""Deterministický Quant Engine – ROI, citlivost, Monte Carlo.

Pravidlo: LLM nikdy nevyrábí čísla. Všechny výpočty jsou deterministické
a plně auditovatelné. Vstupy pocházejí z dat klienta nebo explicitně
označených předpokladů (Assumption).
"""
from __future__ import annotations

from typing import Any


class QuantEngine:
    """Hlavní vstup do Quant Enginu. Deleguje na specializované výpočty."""

    def compute_roi(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Vypočítá návratnost investice (ROI).

        Očekávané klíče ve vstupu:
          - investment: počáteční investice (float)
          - annual_return: roční návratnost / úspora (float)
          - years: délka období v letech (int)
          - discount_rate: diskontní sazba v desítkách (např. 0.08 = 8 %)

        Vrací dict s ROI, NPV, payback obdobím a cash flow.
        """
        investment = float(inputs.get("investment", 0))
        annual_return = float(inputs.get("annual_return", 0))
        years = int(inputs.get("years", 1))
        discount_rate = float(inputs.get("discount_rate", 0))

        if investment <= 0:
            return {
                "roi": None,
                "npv": None,
                "payback_years": None,
                "cash_flow": [],
                "status": "error: investment must be > 0",
            }

        cash_flow = []
        cumulative = -investment
        npv = -investment
        payback_years = None

        for year in range(1, years + 1):
            net_cash = annual_return
            cumulative += net_cash
            npv += net_cash / ((1 + discount_rate) ** year)
            cash_flow.append(
                {
                    "year": year,
                    "cash_flow": net_cash,
                    "cumulative": cumulative,
                    "npv_contribution": net_cash / ((1 + discount_rate) ** year),
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
        """Citlivostní analýza: jak se změna vstupního předpokladu promítne do ROI.

        Vstup: base_case + variations (seznam změn klíčů s novými hodnotami).
        Vrací seznam výsledků pro každou variaci.
        """
        base_case = inputs.get("base_case", {})
        variations = inputs.get("variations", [])

        base_result = self.compute_roi(base_case)
        results = []

        for variation in variations:
            name = variation.get("name", "unknown")
            modified = dict(base_case)
            for key, value in variation.get("changes", {}).items():
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
                    "changes": variation.get("changes", {}),
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