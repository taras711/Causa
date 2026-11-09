"""Unit testy pro quant/monte_carlo.py — simulace, seed reprodukovatelnost."""

from __future__ import annotations

from src.quant.monte_carlo import MonteCarlo


def test_monte_carlo_default_iterations() -> None:
    mc = MonteCarlo()
    model = {
        "investment_range": [80000, 120000],
        "annual_return_range": [20000, 40000],
        "years": 5,
        "discount_rate_range": [0.05, 0.12],
    }
    result = mc.simulate(model=model, iterations=200, seed=42)
    assert result["status"] == "ok"
    assert result["iterations"] == 200
    assert 0 <= result["positive_roi_probability"] <= 100
    assert result["roi_min"] is not None
    assert result["roi_max"] is not None
    assert result["roi_median"] is not None
    assert result["roi_p10"] is not None
    assert result["roi_p90"] is not None
    assert result["roi_min"] <= result["roi_median"] <= result["roi_max"]
    assert len(result["results"]) == 200


def test_monte_carlo_seed_reproducible() -> None:
    model = {
        "investment_range": [80000, 120000],
        "annual_return_range": [20000, 40000],
        "years": 5,
        "discount_rate_range": [0.05, 0.12],
    }
    r1 = MonteCarlo().simulate(model=model, iterations=100, seed=7)
    r2 = MonteCarlo().simulate(model=model, iterations=100, seed=7)
    assert r1["roi_min"] == r2["roi_min"]
    assert r1["roi_max"] == r2["roi_max"]
    assert r1["positive_roi_probability"] == r2["positive_roi_probability"]


def test_monte_carlo_no_positive_roi() -> None:
    mc = MonteCarlo()
    model = {
        "investment_range": [1000000, 1000000],
        "annual_return_range": [1000, 1000],
        "years": 1,
        "discount_rate_range": [0.1, 0.1],
    }
    result = mc.simulate(model=model, iterations=50, seed=1)
    assert result["positive_roi_probability"] == 0.0
    assert result["roi_max"] < 0
