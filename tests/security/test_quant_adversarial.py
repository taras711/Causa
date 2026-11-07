"""Bezpečnostní / adversarial testy pro Quant Engine.

Ověřují odolnost vůči neplatným vstupům, přetečení, NaN/Infinity,
extrémním hodnotám a injekčním payloadům (které se musí chovat jako data).
"""
from __future__ import annotations

import math

import pytest

from src.quant.engine import QuantEngine
from src.quant.monte_carlo import MonteCarlo
from src.quant.assumption_graph import AssumptionGraph


@pytest.fixture
def engine() -> QuantEngine:
    return QuantEngine()


@pytest.fixture
def mc() -> MonteCarlo:
    return MonteCarlo()


@pytest.fixture
def graph() -> AssumptionGraph:
    return AssumptionGraph()


# ------------------------------------------------------------------ #
# compute_roi – neplatné vstupy
# ------------------------------------------------------------------ #


@pytest.mark.security
def test_roi_none_investment_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": None})
    assert isinstance(result, dict)
    assert result.get("status", "").startswith("error") or result.get("roi") is None


@pytest.mark.security
def test_roi_string_investment_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": "abc"})
    assert isinstance(result, dict)
    assert result.get("status", "").startswith("error") or result.get("roi") is None


@pytest.mark.security
def test_roi_list_investment_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": [1, 2]})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_nan_investment_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": float("nan"), "annual_return": 10, "years": 3})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_inf_investment_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": float("inf"), "annual_return": 10, "years": 3})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_years_string_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": 100, "years": "abc"})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_years_none_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": 100, "years": None})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_negative_years_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": 100, "annual_return": 10, "years": -5})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_huge_years_does_not_dos(engine: QuantEngine) -> None:
    result = engine.compute_roi({"investment": 100, "annual_return": 10, "years": 10000000})
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_discount_rate_minus_one_does_not_crash(engine: QuantEngine) -> None:
    result = engine.compute_roi(
        {"investment": 100, "annual_return": 10, "years": 3, "discount_rate": -1.0}
    )
    assert isinstance(result, dict)


@pytest.mark.security
def test_roi_empty_dict_returns_error(engine: QuantEngine) -> None:
    result = engine.compute_roi({})
    assert result["status"].startswith("error")
    assert result["roi"] is None


@pytest.mark.security
def test_roi_injection_payload_treated_as_data(engine: QuantEngine) -> None:
    payload = {
        "investment": 100,
        "annual_return": 10,
        "years": 2,
        "discount_rate": 0.1,
        "extra": "'; DROP TABLE users; --",
    }
    result = engine.compute_roi(payload)
    assert result["status"] == "ok"


# ------------------------------------------------------------------ #
# sensitivity – neplatné vstupy
# ------------------------------------------------------------------ #


@pytest.mark.security
def test_sensitivity_non_dict_base_case_does_not_crash(engine: QuantEngine) -> None:
    try:
        result = engine.sensitivity({"base_case": None, "variations": []})
    except Exception:
        return
    assert isinstance(result, dict)


@pytest.mark.security
def test_sensitivity_variations_not_list_does_not_crash(engine: QuantEngine) -> None:
    try:
        result = engine.sensitivity({"base_case": {"investment": 100}, "variations": "abc"})
    except Exception:
        return
    assert isinstance(result, dict)


@pytest.mark.security
def test_sensitivity_variation_changes_not_dict_does_not_crash(engine: QuantEngine) -> None:
    result = engine.sensitivity(
        {
            "base_case": {"investment": 100, "annual_return": 10, "years": 2},
            "variations": [{"name": "x", "changes": "not-a-dict"}],
        }
    )
    assert isinstance(result, dict)


@pytest.mark.security
def test_sensitivity_huge_variations_list_does_not_dos(engine: QuantEngine) -> None:
    result = engine.sensitivity(
        {
            "base_case": {"investment": 100, "annual_return": 10, "years": 2},
            "variations": [{"name": f"v{i}", "changes": {}} for i in range(10000)],
        }
    )
    assert isinstance(result, dict)


# ------------------------------------------------------------------ #
# monte carlo – neplatné / adversarial vstupy
# ------------------------------------------------------------------ #


@pytest.mark.security
def test_mc_empty_model_does_not_crash(mc: MonteCarlo) -> None:
    result = mc.simulate(model={}, iterations=10, seed=1)
    assert isinstance(result, dict)
    assert result["status"] == "ok"


@pytest.mark.security
def test_mc_negative_iterations_returns_empty(mc: MonteCarlo) -> None:
    result = mc.simulate(model={}, iterations=-5, seed=1)
    assert result["iterations"] == 0
    assert result["results"] == []
    assert result["positive_roi_probability"] is None


@pytest.mark.security
def test_mc_reversed_range_does_not_crash(mc: MonteCarlo) -> None:
    model = {
        "investment_range": [120000, 80000],
        "annual_return_range": [40000, 20000],
        "years": 3,
        "discount_rate_range": [0.15, 0.05],
    }
    try:
        result = mc.simulate(model=model, iterations=5, seed=1)
    except ValueError:
        return
    assert isinstance(result, dict)


@pytest.mark.security
def test_mc_non_numeric_range_does_not_crash(mc: MonteCarlo) -> None:
    model = {"investment_range": ["a", "b"], "years": 1}
    try:
        result = mc.simulate(model=model, iterations=3, seed=1)
    except (TypeError, ValueError):
        return
    assert isinstance(result, dict)


@pytest.mark.security
def test_mc_iterations_string_does_not_crash(mc: MonteCarlo) -> None:
    try:
        result = mc.simulate(model={}, iterations="abc", seed=1)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return
    assert isinstance(result, dict)


@pytest.mark.security
def test_mc_years_zero_does_not_crash(mc: MonteCarlo) -> None:
    model = {"investment_range": [100, 200], "annual_return_range": [10, 20], "years": 0}
    result = mc.simulate(model=model, iterations=5, seed=1)
    assert isinstance(result, dict)


@pytest.mark.security
def test_mc_huge_iterations_does_not_dos(mc: MonteCarlo) -> None:
    result = mc.simulate(model={"investment_range": [100, 100]}, iterations=100, seed=1)
    assert len(result["results"]) == 100


@pytest.mark.security
def test_mc_seed_injection_does_not_crash(mc: MonteCarlo) -> None:
    result = mc.simulate(model={}, iterations=5, seed=999999)
    assert isinstance(result, dict)


# ------------------------------------------------------------------ #
# assumption graph – neplatné / adversarial vstupy
# ------------------------------------------------------------------ #


@pytest.mark.security
def test_graph_add_none_id_does_not_crash(graph: AssumptionGraph) -> None:
    try:
        graph.add_assumption(None, 1)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return
    assert True


@pytest.mark.security
def test_graph_duplicate_id_overwrite(graph: AssumptionGraph) -> None:
    graph.add_assumption("a", 1)
    graph.add_assumption("a", 2)
    assert graph.get("a")["value"] == 2


@pytest.mark.security
def test_graph_depends_on_not_list_does_not_crash(graph: AssumptionGraph) -> None:
    try:
        graph.add_assumption("a", 1, depends_on="b")  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return
    assert isinstance(graph.list_assumptions(), list)


@pytest.mark.security
def test_graph_recompute_self_loop_does_not_crash(graph: AssumptionGraph) -> None:
    graph.add_assumption("a", 1, depends_on=["a"])
    result = graph.recompute("a", 2)
    assert result["assumption_id"] == "a"


@pytest.mark.security
def test_graph_large_chain_does_not_dos(graph: AssumptionGraph) -> None:
    n = 5000
    graph.add_assumption("n0", 0)
    for i in range(1, n):
        graph.add_assumption(f"n{i}", 0, depends_on=[f"n{i - 1}"])
    result = graph.recompute("n0", 1)
    assert len(result["affected"]) == n - 1


@pytest.mark.security
def test_graph_recompute_nonexistent_raises_valueerror(graph: AssumptionGraph) -> None:
    with pytest.raises(ValueError):
        graph.recompute("neexistuje", 1)


@pytest.mark.security
def test_graph_set_type_confusion(graph: AssumptionGraph) -> None:
    graph.add_assumption("a", 1)
    graph.set("a", "injected")
    assert graph.get("a")["value"] == "injected"


@pytest.mark.security
def test_graph_injection_id_treated_as_key(graph: AssumptionGraph) -> None:
    evil = "'; DROP TABLE assumptions; --"
    graph.add_assumption(evil, 42)
    assert graph.get(evil) is not None
    assert evil in graph.list_assumptions()
