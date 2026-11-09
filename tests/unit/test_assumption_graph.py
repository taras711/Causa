"""Unit testy pro AssumptionGraph (graf předpokladů s přepočtem)."""

from __future__ import annotations

import pytest

from src.quant.assumption_graph import AssumptionGraph


@pytest.fixture
def graph() -> AssumptionGraph:
    return AssumptionGraph()


# ------------------------------------------------------------------ #
# add_assumption a get
# ------------------------------------------------------------------ #

def test_add_and_get_assumption(graph: AssumptionGraph) -> None:
    """Přidání a načtení předpokladu."""
    graph.add_assumption("diskontni_sazba", 0.1)
    assert graph.get("diskontni_sazba") == {"value": 0.1, "depends_on": []}


def test_add_assumption_with_dependencies(graph: AssumptionGraph) -> None:
    """Předpoklad může mít závislosti na jiných předpokladech."""
    graph.add_assumption("investice", 100_000)
    graph.add_assumption("rocni_navratnost", 30_000, depends_on=["investice"])
    assert graph.get("rocni_navratnost")["depends_on"] == ["investice"]


def test_get_nonexistent_assumption(graph: AssumptionGraph) -> None:
    """Načtení neexistujícího předpokladu vrací None."""
    assert graph.get("neexistuje") is None


def test_list_assumptions(graph: AssumptionGraph) -> None:
    """list_assumptions vrací seřazený seznam ID všech předpokladů."""
    assert graph.list_assumptions() == []
    graph.add_assumption("b", 2)
    graph.add_assumption("a", 1)
    graph.add_assumption("c", 3)
    assert graph.list_assumptions() == ["a", "b", "c"]


# ------------------------------------------------------------------ #
# set a recompute
# ------------------------------------------------------------------ #

def test_set_assumption(graph: AssumptionGraph) -> None:
    """Změna hodnoty existujícího předpokladu."""
    graph.add_assumption("sazba", 0.05)
    graph.set("sazba", 0.12)
    assert graph.get("sazba")["value"] == 0.12


def test_set_nonexistent_assumption_raises(graph: AssumptionGraph) -> None:
    """Změna neexistujícího předpokladu vyhodí ValueError."""
    with pytest.raises(ValueError, match="neexistuje"):
        graph.set("neexistuje", 999)


def test_recompute_returns_affected(graph: AssumptionGraph) -> None:
    """recompute změní hodnotu a vrátí seznam ovlivněných předpokladů."""
    graph.add_assumption("zakladni_investice", 100_000)
    graph.add_assumption("odvodena_metrika", 0, depends_on=["zakladni_investice"])
    graph.add_assumption("dalsi_metrika", 0, depends_on=["odvodena_metrika"])

    result = graph.recompute("zakladni_investice", 200_000)

    assert result["assumption_id"] == "zakladni_investice"
    assert result["new_value"] == 200_000
    assert graph.get("zakladni_investice")["value"] == 200_000
    assert "odvodena_metrika" in result["affected"]
    assert "dalsi_metrika" in result["affected"]


def test_recompute_nonexistent_raises(graph: AssumptionGraph) -> None:
    """recompute na neexistující předpoklad vyhodí ValueError."""
    with pytest.raises(ValueError, match="neexistuje"):
        graph.recompute("neexistuje", 999)


def test_recompute_no_dependents(graph: AssumptionGraph) -> None:
    """Předpoklad bez závislých vrací prázdný seznam affected."""
    graph.add_assumption("samostatny", 42)
    result = graph.recompute("samostatny", 99)
    assert result["affected"] == []
    assert graph.get("samostatny")["value"] == 99


# ------------------------------------------------------------------ #
# cykly v grafu (ochrana proti nekonečné rekurzi)
# ------------------------------------------------------------------ #

def test_circular_dependency_does_not_crash(graph: AssumptionGraph) -> None:
    """Přímý cyklus A -> B -> A by neměl způsobit nekonečnou rekurzi."""
    graph.add_assumption("a", 1, depends_on=["b"])
    graph.add_assumption("b", 2, depends_on=["a"])

    result = graph.recompute("a", 10)
    assert result["assumption_id"] == "a"
    assert result["new_value"] == 10
    # affected obsahuje b (a případně znovu a přes visited ochranu)
    assert "b" in result["affected"]