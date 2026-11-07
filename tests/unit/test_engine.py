"""Unit testy pro WorkflowEngine (checkpointy, durable execution)."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.core.case import Case, CaseStatus, CaseStep
from src.core.engine import WorkflowEngine
from src.core.ledger import Ledger


@pytest.fixture
def db_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def ledger(db_path: str) -> Ledger:
    # Ledger používá vlastní cesty, vytvoříme jiný dočasný soubor
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.unlink(path)  # Ledger si soubor sám vytvoří
    return Ledger(db_path=path)


def _register_case_steps(engine: WorkflowEngine) -> None:
    call_order: list[str] = []

    def step_a(case: Case) -> str:
        call_order.append("a")
        case.add_claim(text="Claim from step A", source="work_model")
        return "result-a"

    def step_b(case: Case) -> str:
        call_order.append("b")
        case.add_claim(text="Claim from step B", source="client_data")
        return "result-b"

    def step_c(case: Case) -> str:
        call_order.append("c")
        raise RuntimeError("krok C selhal záměrně")

    engine.register_step("step_a", step_a)
    engine.register_step("step_b", step_b)
    engine.register_step("step_c", step_c)
    return call_order


def test_engine_runs_all_steps_and_checkpoints(
    db_path: str, ledger: Ledger
) -> None:
    engine = WorkflowEngine(db_path=db_path, ledger=ledger)
    call_order = _register_case_steps(engine)

    case = Case(case_id="case-1", title="Test case", plan=["step_a", "step_b"])
    result_case = engine.run_case(case)

    assert result_case.status == CaseStatus.COMPLETED
    assert result_case.completed_steps == ["step_a", "step_b"]
    assert call_order == ["a", "b"]
    assert len(result_case.claims) == 2


def test_engine_skips_completed_steps_on_resume(
    db_path: str, ledger: Ledger
) -> None:
    engine = WorkflowEngine(db_path=db_path, ledger=ledger)
    call_order = _register_case_steps(engine)

    # První běh – dokončí jen step_a
    case = Case(case_id="case-1", title="Test case", plan=["step_a", "step_b"])
    # Manipulujeme: step_a už je dokončený
    case.completed_steps.append("step_a")
    case.status = CaseStatus.RUNNING
    result_case = engine.run_case(case)

    # step_a by měl být přeskočen, step_b spuštěn
    assert result_case.status == CaseStatus.COMPLETED
    assert result_case.completed_steps == ["step_a", "step_b"]
    assert call_order == ["b"]  # step_a byl přeskočen


def test_engine_records_step_started_and_completed_in_ledger(
    db_path: str, ledger: Ledger
) -> None:
    engine = WorkflowEngine(db_path=db_path, ledger=ledger)

    def step_a(case: Case) -> str:
        return "ok"

    engine.register_step("step_a", step_a)

    case = Case(case_id="case-1", title="Test", plan=["step_a"])
    engine.run_case(case)

    entries = ledger.get_for_case("case-1")
    events = [e["event"] for e in entries]
    assert "step_started" in events
    assert "step_completed" in events


def test_engine_raises_on_failed_step(
    db_path: str, ledger: Ledger
) -> None:
    engine = WorkflowEngine(db_path=db_path, ledger=ledger)

    def failing_step(case: Case) -> str:
        raise ValueError("něco se pokazilo")

    engine.register_step("failing", failing_step)

    case = Case(case_id="case-1", title="Test", plan=["failing"])
    with pytest.raises(ValueError, match="něco se pokazilo"):
        engine.run_case(case)

    steps = [s for s in case.steps if s.step_name == "failing"]
    assert len(steps) == 1
    assert steps[0].status == "failed"
    assert steps[0].error == "něco se pokazilo"
    assert case.status != CaseStatus.COMPLETED


def test_engine_ledger_records_failure(
    db_path: str, ledger: Ledger
) -> None:
    engine = WorkflowEngine(db_path=db_path, ledger=ledger)

    def failing_step(case: Case) -> str:
        raise RuntimeError("selhání")

    engine.register_step("failing", failing_step)

    case = Case(case_id="case-1", title="Test", plan=["failing"])
    with pytest.raises(RuntimeError):
        engine.run_case(case)

    entries = ledger.get_for_case("case-1")
    events = [e["event"] for e in entries]
    assert "step_failed" in events