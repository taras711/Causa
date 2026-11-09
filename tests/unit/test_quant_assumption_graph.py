"""Unit testy pro quant/assumption_graph.py — graf předpokladů a závislostí."""

from __future__ import annotations

from src.quant.assumption_graph import AssumptionGraph


def test_add_and_get_assumption() -> None:
    graph = AssumptionGraph()
    graph.add_assumption("discount_rate", 0.08)
    graph.add_assumption("annual_return", 30000)

    assert graph.get("discount_rate")["value"] == 0.08
    assert graph.get("annual_return")["value"] == 30000
    assert graph.get("nonexistent") is None


def test_set_assumption_raises_when_missing() -> None:
    graph = AssumptionGraph()
    try:
        graph.set("missing", 42)
        assert False, "měl by vyhodit ValueError"
    except ValueError:
        pass


def test_recompute_and_affected() -> None:
    graph = AssumptionGraph()
    graph.add_assumption("base_investment", 100000)
    graph.add_assumption("roi", 25.0, depends_on=["base_investment"])
    graph.add_assumption("npv", 50000, depends_on=["base_investment", "roi"])

    result = graph.recompute("base_investment", 150000)
    assert result["assumption_id"] == "base_investment"
    assert result["new_value"] == 150000
    assert "roi" in result["affected"]
    assert "npv" in result["affected"]


def test_list_assumptions_sorted() -> None:
    graph = AssumptionGraph()
    graph.add_assumption("zebra", 1)
    graph.add_assumption("alpha", 2)
    graph.add_assumption("mid", 3)
    assert graph.list_assumptions() == ["alpha", "mid", "zebra"]
