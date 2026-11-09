"""Unit testy pro Monte Carlo simulaci v Quant Enginu."""

from __future__ import annotations

import pytest

from src.quant.monte_carlo import MonteCarlo
from src.quant.engine import QuantEngine


@pytest.fixture
def monte_carlo() -> MonteCarlo:
    return MonteCarlo()


@pytest.fixture
def base_model() -> dict:
    return {
        "investment_range": [80_000, 120_000],
        "annual_return_range": [20_000, 40_000],
        "years": 5,
        "discount_rate_range": [0.05, 0.15],
    }


# ------------------------------------------------------------------ #
# simulate – základní scénáře
# ------------------------------------------------------------------ #

def test_monte_carlo_basic(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Základní simulace vrací distribuci výsledků."""
    result = monte_carlo.simulate(model=base_model, iterations=100, seed=42)

    assert result["status"] == "ok"
    assert result["iterations"] == 100
    assert result["roi_min"] is not None
    assert result["roi_max"] is not None
    assert result["roi_median"] is not None
    assert result["roi_p10"] is not None
    assert result["roi_p90"] is not None
    assert result["positive_roi_probability"] is not None
    assert 0 <= result["positive_roi_probability"] <= 100
    assert result["roi_min"] <= result["roi_median"] <= result["roi_max"]
    assert result["roi_p10"] <= result["roi_p90"]


def test_monte_carlo_deterministic_with_seed(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Stejný seed produkuje stejné výsledky (determinismus)."""
    result_a = monte_carlo.simulate(model=base_model, iterations=100, seed=42)
    result_b = monte_carlo.simulate(model=base_model, iterations=100, seed=42)

    assert result_a["roi_min"] == result_b["roi_min"]
    assert result_a["roi_max"] == result_b["roi_max"]
    assert result_a["roi_median"] == result_b["roi_median"]
    assert result_a["positive_roi_probability"] == result_b["positive_roi_probability"]


def test_monte_carlo_different_seed_different_results(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Různé seedy mohou produkovat mírně odlišné výsledky."""
    result_a = monte_carlo.simulate(model=base_model, iterations=500, seed=1)
    result_b = monte_carlo.simulate(model=base_model, iterations=500, seed=2)

    # S 500 iteracemi je velmi pravděpodobné, že se výsledky liší
    assert result_a["roi_min"] != result_b["roi_min"] or result_a["roi_max"] != result_b["roi_max"]


def test_monte_carlo_positive_roi_probability_range(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Pravděpodobnost kladného ROI je v rozsahu 0–100 %."""
    result = monte_carlo.simulate(model=base_model, iterations=200, seed=7)
    assert 0.0 <= result["positive_roi_probability"] <= 100.0


def test_monte_carlo_results_length_matches_iterations(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Počet výsledků odpovídá počtu iterací."""
    result = monte_carlo.simulate(model=base_model, iterations=50, seed=3)
    assert len(result["results"]) == 50


def test_monte_carlo_result_entry_structure(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Každá položka výsledků obsahuje očekávané klíče."""
    result = monte_carlo.simulate(model=base_model, iterations=10, seed=1)
    for entry in result["results"]:
        assert "investment" in entry
        assert "annual_return" in entry
        assert "discount_rate" in entry
        assert "roi" in entry
        assert "npv" in entry
        assert "payback_years" in entry
        assert 80_000 <= entry["investment"] <= 120_000
        assert 20_000 <= entry["annual_return"] <= 40_000
        assert 0.05 <= entry["discount_rate"] <= 0.15


def test_monte_carlo_default_iterations(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Výchozí počet iterací je 1000."""
    result = monte_carlo.simulate(model=base_model, seed=5)
    assert result["iterations"] == 1000
    assert len(result["results"]) == 1000


def test_monte_carlo_zero_iterations(monte_carlo: MonteCarlo, base_model: dict) -> None:
    """Nula iterací – prázdné výsledky, žádné percentile."""
    result = monte_carlo.simulate(model=base_model, iterations=0, seed=1)
    assert result["iterations"] == 0
    assert result["results"] == []
    assert result["roi_min"] is None
    assert result["roi_max"] is None
    assert result["roi_median"] is None


def test_monte_carlo_all_positive_returns(monte_carlo: MonteCarlo) -> None:
    """Když jsou všechny návratnosti vysoké, pravděpodobnost kladného ROI je 100 %."""
    model = {
        "investment_range": [10_000, 20_000],
        "annual_return_range": [50_000, 60_000],
        "years": 3,
        "discount_rate_range": [0.0, 0.1],
    }
    result = monte_carlo.simulate(model=model, iterations=100, seed=1)
    assert result["positive_roi_probability"] == 100.0


def test_monte_carlo_all_negative_returns(monte_carlo: MonteCarlo) -> None:
    """Když jsou všechny návratnosti nulové, pravděpodobnost kladného ROI je 0 %."""
    model = {
        "investment_range": [100_000, 200_000],
        "annual_return_range": [0, 0],
        "years": 3,
        "discount_rate_range": [0.0, 0.1],
    }
    result = monte_carlo.simulate(model=model, iterations=100, seed=1)
    assert result["positive_roi_probability"] == 0.0
    # Při annual_return=0 je kumulativní cash flow = -investice, tudíž ROI = -100 %
    assert result["roi_max"] == -100.0