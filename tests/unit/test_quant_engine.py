"""Unit testy pro Quant Engine (ROI, citlivostní analýza).

Všechny výpočty jsou deterministické – LLM nevyrábí čísla.
"""

from __future__ import annotations

import pytest

from src.quant.engine import QuantEngine


@pytest.fixture
def engine() -> QuantEngine:
    return QuantEngine()


# ------------------------------------------------------------------ #
# compute_roi – základní scénáře
# ------------------------------------------------------------------ #

def test_compute_roi_basic(engine: QuantEngine) -> None:
    """Základní výpočet ROI s kladnou návratností."""
    result = engine.compute_roi(
        {
            "investment": 100_000,
            "annual_return": 30_000,
            "years": 5,
            "discount_rate": 0.1,
        }
    )

    assert result["status"] == "ok"
    assert result["investment"] == 100_000
    assert result["annual_return"] == 30_000
    assert result["years"] == 5
    assert result["discount_rate"] == 0.1
    assert result["roi"] is not None
    assert result["npv"] is not None
    assert result["payback_years"] is not None
    assert result["payback_years"] == 4
    assert len(result["cash_flow"]) == 5


def test_compute_roi_positive_roi(engine: QuantEngine) -> None:
    """ROI by měl být kladný při dostatečné návratnosti."""
    result = engine.compute_roi(
        {"investment": 100_000, "annual_return": 50_000, "years": 3, "discount_rate": 0.05}
    )
    assert result["roi"] > 0


def test_compute_roi_negative_roi(engine: QuantEngine) -> None:
    """ROI může být záporný, pokud návratnost nepokryje investici."""
    result = engine.compute_roi(
        {"investment": 100_000, "annual_return": 10_000, "years": 3, "discount_rate": 0.05}
    )
    assert result["roi"] < 0


def test_compute_roi_investment_zero_returns_error(engine: QuantEngine) -> None:
    """Investice 0 by měla vracet chybový stav."""
    result = engine.compute_roi(
        {"investment": 0, "annual_return": 10_000, "years": 3, "discount_rate": 0.05}
    )
    assert result["status"] == "error: investment must be > 0"
    assert result["roi"] is None
    assert result["npv"] is None


def test_compute_roi_investment_negative_returns_error(engine: QuantEngine) -> None:
    """Záporná investice by měla vracet chybový stav."""
    result = engine.compute_roi(
        {"investment": -50_000, "annual_return": 10_000, "years": 3, "discount_rate": 0.05}
    )
    assert result["status"] == "error: investment must be > 0"


def test_compute_roi_zero_years(engine: QuantEngine) -> None:
    """Nulové období – žádné cash flow, payback None."""
    result = engine.compute_roi(
        {"investment": 100_000, "annual_return": 10_000, "years": 0, "discount_rate": 0.05}
    )
    assert result["status"] == "ok"
    assert result["cash_flow"] == []
    assert result["payback_years"] is None


def test_compute_roi_defaults(engine: QuantEngine) -> None:
    """Výchozí hodnoty: investment=0, annual_return=0, years=1, discount_rate=0."""
    result = engine.compute_roi({})
    assert result["status"] == "error: investment must be > 0"


def test_compute_roi_cash_flow_structure(engine: QuantEngine) -> None:
    """Každý položka cash_flow obsahuje očekávané klíče."""
    result = engine.compute_roi(
        {"investment": 50_000, "annual_return": 20_000, "years": 3, "discount_rate": 0.08}
    )
    for entry in result["cash_flow"]:
        assert "year" in entry
        assert "cash_flow" in entry
        assert "cumulative" in entry
        assert "npv_contribution" in entry
    assert result["cash_flow"][0]["year"] == 1
    assert result["cash_flow"][-1]["year"] == 3


def test_compute_roi_payback_never_reached(engine: QuantEngine) -> None:
    """Pokud kumulativní cash flow nikdy neklesne pod nulu, payback je None."""
    result = engine.compute_roi(
        {"investment": 100_000, "annual_return": 10_000, "years": 5, "discount_rate": 0.05}
    )
    assert result["payback_years"] is None


# ------------------------------------------------------------------ #
# sensitivity – citlivostní analýza
# ------------------------------------------------------------------ #

def test_sensitivity_basic(engine: QuantEngine) -> None:
    """Základní citlivostní analýza s jednou variací."""
    result = engine.sensitivity(
        {
            "base_case": {
                "investment": 100_000,
                "annual_return": 30_000,
                "years": 5,
                "discount_rate": 0.1,
            },
            "variations": [
                {
                    "name": "vyšší diskontní sazba",
                    "changes": {"discount_rate": 0.15},
                },
                {
                    "name": "nižší roční návratnost",
                    "changes": {"annual_return": 20_000},
                },
            ],
        }
    )

    assert result["status"] == "ok"
    assert result["base_roi"] is not None
    assert len(result["results"]) == 2

    names = {r["variation"] for r in result["results"]}
    assert names == {"vyšší diskontní sazba", "nižší roční návratnost"}

    # Diskontní sazba neovlivňuje ROI (pouze NPV), takže roi_delta je 0.0
    high_discount = next(r for r in result["results"] if r["variation"] == "vyšší diskontní sazba")
    assert high_discount["roi_delta"] == 0.0

    # Nižší roční návratnost sníží ROI (žádná změna NPV)
    lower_return = next(r for r in result["results"] if r["variation"] == "nižší roční návratnost")
    assert lower_return["roi_delta"] is not None
    assert lower_return["roi_delta"] < 0


def test_sensitivity_empty_variations(engine: QuantEngine) -> None:
    """Prázdný seznam variací vrací jen base case bez výsledků."""
    result = engine.sensitivity(
        {
            "base_case": {
                "investment": 100_000,
                "annual_return": 30_000,
                "years": 5,
                "discount_rate": 0.1,
            },
            "variations": [],
        }
    )
    assert result["results"] == []
    assert result["base_roi"] is not None


def test_sensitivity_empty_base_case(engine: QuantEngine) -> None:
    """Prázdný base_case – investment 0 → chybový stav v base i variacích."""
    result = engine.sensitivity({"base_case": {}, "variations": []})
    assert result["base_roi"] is None
    assert result["results"] == []


def test_sensitivity_variation_changes_applied(engine: QuantEngine) -> None:
    """Změny v variaci se projeví ve výsledném ROI."""
    result = engine.sensitivity(
        {
            "base_case": {
                "investment": 100_000,
                "annual_return": 30_000,
                "years": 5,
                "discount_rate": 0.1,
            },
            "variations": [
                {
                    "name": "investice 200 000",
                    "changes": {"investment": 200_000},
                },
            ],
        }
    )
    varied = result["results"][0]
    assert varied["roi"] is not None
    assert varied["roi_delta"] is not None
    assert varied["roi_delta"] < 0  # vyšší investice při stejné návratnosti = nižší ROI


def test_sensitivity_roi_delta_none_when_base_error(engine: QuantEngine) -> None:
    """Pokud base case selže (investice <= 0), roi_delta je None."""
    result = engine.sensitivity(
        {
            "base_case": {"investment": 0, "annual_return": 10_000, "years": 3, "discount_rate": 0.05},
            "variations": [
                {"name": "oprava investice", "changes": {"investment": 50_000}}
            ],
        }
    )
    assert result["base_roi"] is None
    varied = result["results"][0]
    assert varied["roi_delta"] is None
    # Ale samotná variace může být OK
    assert varied["roi"] is not None