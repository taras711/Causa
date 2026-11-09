"""Integrační testy: WorkflowEngine + Case + Ledger end-to-end."""

from __future__ import annotations

import sqlite3
import tempfile

import pytest

from src.core.case import Case, CaseStatus, CaseStep
from src.core.engine import WorkflowEngine
from src.core.ledger import Ledger


_CASES_DDL = """
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    plan TEXT NOT NULL,
    completed_steps TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


class TestWorkflowEngineEndToEnd:
    """Celý životní cyklus případu přes engine s checkpointy v ledgeru."""

    def _make_engine(self, tmp: str) -> tuple[WorkflowEngine, Ledger]:
        db_path = f"{tmp}/engine.db"
        # Vytvorit tabulku cases, kterou WorkflowEngine pouziva k persistenci
        conn = sqlite3.connect(db_path)
        conn.execute(_CASES_DDL)
        conn.commit()
        conn.close()
        ledger = Ledger(f"{tmp}/ledger.db")
        return WorkflowEngine(db_path, ledger), ledger

    def test_successful_run_completes_all_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine, ledger = self._make_engine(tmp)

            case = Case(
                case_id="case-e2e-1",
                title="Úspěšný běh",
                tenant_id="tenant-acme",
                plan=["framer", "diagnostician", "verifier"],
            )

            calls: list[str] = []

            def framer(case: Case) -> str:
                calls.append("framer")
                return "scope defined"

            def diagnostician(case: Case) -> str:
                calls.append("diagnostician")
                return "root causes found"

            def verifier(case: Case) -> str:
                calls.append("verifier")
                return "verified"

            engine.register_step("framer", framer)
            engine.register_step("diagnostician", diagnostician)
            engine.register_step("verifier", verifier)

            result = engine.run_case(case)

            assert result.status == CaseStatus.COMPLETED
            assert result.completed_steps == ["framer", "diagnostician", "verifier"]
            assert calls == ["framer", "diagnostician", "verifier"]

            # Ledger obsahuje checkpointy pro všechny kroky
            records = ledger.get_for_case("case-e2e-1")
            events = [r["event"] for r in records]
            assert events.count("step_started") == 3
            assert events.count("step_completed") == 3

    def test_failed_step_sets_case_status_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine, ledger = self._make_engine(tmp)

            case = Case(
                case_id="case-e2e-2",
                title="Selhání kroku",
                tenant_id="tenant-acme",
                plan=["step-a", "step-b"],
            )

            def step_a(case: Case) -> str:
                raise RuntimeError("something broke")

            def step_b(case: Case) -> str:
                return "should not run"

            engine.register_step("step-a", step_a)
            engine.register_step("step-b", step_b)

            with pytest.raises(RuntimeError, match="something broke"):
                engine.run_case(case)

            assert case.status == CaseStatus.FAILED
            assert case.completed_steps == []

            # Ledger zaznamená selhání
            records = ledger.get_for_case("case-e2e-2")
            events = [r["event"] for r in records]
            assert "step_failed" in events
            assert "step_completed" not in events

    def test_completed_steps_are_skipped_on_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine, ledger = self._make_engine(tmp)

            case = Case(
                case_id="case-e2e-3",
                title="Přeskočení hotových kroků",
                tenant_id="tenant-acme",
                plan=["step-1", "step-2"],
            )

            calls: list[str] = []

            def step_1(case: Case) -> str:
                calls.append("step-1")
                return "done-1"

            def step_2(case: Case) -> str:
                calls.append("step-2")
                return "done-2"

            engine.register_step("step-1", step_1)
            engine.register_step("step-2", step_2)

            # První běh
            engine.run_case(case)
            assert calls == ["step-1", "step-2"]
            assert case.status == CaseStatus.COMPLETED

            # Druhý běh – všechny kroky už hotové, nic se neopakuje
            calls.clear()
            engine.run_case(case)
            assert calls == []
            assert case.status == CaseStatus.COMPLETED

    def test_case_step_records_contain_result_and_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine, _ = self._make_engine(tmp)

            case = Case(
                case_id="case-e2e-4",
                title="Krok s výsledkem i chybou",
                tenant_id="tenant-acme",
                plan=["ok", "fail"],
            )

            def ok_step(case: Case) -> str:
                return "success"

            def fail_step(case: Case) -> str:
                raise ValueError("boom")

            engine.register_step("ok", ok_step)
            engine.register_step("fail", fail_step)

            try:
                engine.run_case(case)
            except ValueError:
                pass

            ok_step_obj = case.steps[0]
            fail_step_obj = case.steps[1]

            assert ok_step_obj.status == "completed"
            assert ok_step_obj.result == "success"
            assert fail_step_obj.status == "failed"
            assert fail_step_obj.error == "boom"
            assert isinstance(ok_step_obj, CaseStep)
            assert isinstance(fail_step_obj, CaseStep)
