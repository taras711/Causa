"""Unit testy pro quant/engine.py — deterministický ROI, citlivost, edge cases."""

from __future__ import annotations

from src.quant.engine import QuantEngine


def test_compute_roi_basic() -> None:
    engine = QuantEngine()
    result = engine.compute_roi(
        {
            "investment": 100000,
            "annual_return": 30000,
            "years": 5,
            "discount_rate": 0.08,
        }
    )
    assert result["status"] == "ok"
    assert result["investment"] == 100000
    assert result["roi"] is not None
    assert result["npv"] is not None
    assert result["payback_years"] is not None
    assert result["payback_years"] <= 5
    assert len(result["cash_flow"]) == 5


def test_compute_roi_zero_investment() -> None:
    engine = QuantEngine()
    result = engine.compute_roi(
        {"investment": 0, "annual_return": 10000, "years": 3, "discount_rate": 0.05}
    )
    assert result["status"].startswith("error")
    assert result["roi"] is None


def test_compute_roi_negative_investment() -> None:
    engine = QuantEngine()
    result = engine.compute_roi(
        {"investment": -50000, "annual_return": 10000, "years": 3, "discount_rate": 0.05}
    )
    assert result["status"].startswith("error")


def test_compute_roi_payback_never_reached() -> None:
    engine = QuantEngine()
    result = engine.compute_roi(
        {"investment": 1000000, "annual_return": 1000, "years": 5, "discount_rate": 0.05}
    )
    assert result["payback_years"] is None
    assert result["roi"] < 0


def test_compute_roi_cash_flow_structure() -> None:
    engine = QuantEngine()
    result = engine.compute_roi(
        {"investment": 50000, "annual_return": 15000, "years": 3, "discount_rate": 0.1}
    )
    cf = result["cash_flow"]
    assert len(cf) == 3
    assert cf[0]["year"] == 1
    assert cf[0]["cash_flow"] == 15000
    assert cf[0]["cumulative"] == -35000
    assert cf[2]["cumulative"] == -5000


def test_sensitivity_analyze() -> None:
    engine = QuantEngine()
    base = {"investment": 100000, "annual_return": 30000, "years": 5, "discount_rate": 0.08}
    variations = [
        {"name": "vyssi_diskont", "changes": {"discount_rate": 0.12}},
        {"name": "nizsi_vynos", "changes": {"annual_return": 20000}},
    ]
    result = engine.sensitivity({"base_case": base, "variations": variations})
    assert result["status"] == "ok"
    assert result["base_roi"] is not None
    assert len(result["results"]) == 2
    assert result["results"][0]["variation"] == "vyssi_diskont"
    assert result["results"][1]["variation"] == "nizsi_vynos"
    assert "roi_delta" in result["results"][0]


def test_sensitivity_empty_variations() -> None:
    engine = QuantEngine()
    base = {"investment": 100000, "annual_return": 30000, "years": 5, "discount_rate": 0.08}
    result = engine.sensitivity({"base_case": base, "variations": []})
    assert result["results"] == []
    assert result["base_roi"] is not None
