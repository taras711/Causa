"""Unit testy pro quant/sensitivity.py — citlivostní analýza."""

from __future__ import annotations

from src.quant.sensitivity import SensitivityAnalyzer


def test_analyze_returns_variation_results() -> None:
    analyzer = SensitivityAnalyzer()
    base_case = {
        "investment": 100000,
        "annual_return": 30000,
        "years": 5,
        "discount_rate": 0.08,
    }
    variations = [
        {"name": "scenario_high_discount", "changes": {"discount_rate": 0.15}},
        {"name": "scenario_low_return", "changes": {"annual_return": 15000}},
    ]
    results = analyzer.analyze(base_case=base_case, variations=variations)
    assert len(results) == 2
    assert results[0]["variation"] == "scenario_high_discount"
    assert results[1]["variation"] == "scenario_low_return"
    assert results[0]["roi"] is not None
    assert results[1]["roi"] is not None


def test_analyze_empty_variations() -> None:
    analyzer = SensitivityAnalyzer()
    base_case = {"investment": 50000, "annual_return": 10000, "years": 3, "discount_rate": 0.05}
    results = analyzer.analyze(base_case=base_case, variations=[])
    assert results == []
