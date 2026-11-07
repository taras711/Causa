"""Citlivostní analýza – jak se změna předpokladu promítne do výsledku."""
from __future__ import annotations

from typing import Any

from src.quant.engine import QuantEngine


class SensitivityAnalyzer:
    """Spouští citlivostní analýzu nad Quant Enginem."""

    def __init__(self, engine: QuantEngine | None = None) -> None:
        self.engine = engine or QuantEngine()

    def analyze(self, base_case: dict[str, Any], variations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Vrací seznam výsledků citlivosti pro každou variaci.

        Každá variace obsahuje:
          - name: název scénaře
          - changes: dict s klíči a novými hodnotami (např. {"discount_rate": 0.1})
        """
        result = self.engine.sensitivity(
            {"base_case": base_case, "variations": variations}
        )
        return result.get("results", [])