"""Unit testy pro core/engine.py — WorkflowEngine s checkpointy."""

from __future__ import annotations

import os
import sqlite3
import tempfile

from src.core.case import Case, CaseStatus
from src.core.engine import WorkflowEngine
from src.core.ledger import Ledger


def _make_engine() -> tuple[WorkflowEngine, str, str]:
    fd_db, db_path = tempfile.mkstemp(suffix=".db")
    fd_ledger, ledger_path = tempfile.mkstemp(suffix=".db")
    os.close(fd_db)
    os.close(fd_ledger)
    # Vytvorit tabulku cases, kterou WorkflowEngine pouziva k persistenci
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            plan TEXT NOT NULL,
            completed_steps TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    ledger = Ledger(db_path=ledger_path)
    engine = WorkflowEngine(db_path=db_path, ledger=ledger)
    return engine, db_path, ledger_path


def test_workflow_engine_runs_steps_and_checkpoints() -> None:
    engine, db_path, ledger_path = _make_engine()
    try:
        executed: list[str] = []

        def step_a(case: Case) -> str:
            executed.append("a")
            return "result-a"

        def step_b(case: Case) -> str:
            executed.append("b")
            return "result-b"

        engine.register_step("framer", step_a)
        engine.register_step("diagnostician", step_b)

        case = Case(case_id="case-1", title="Test", plan=["framer", "diagnostician"])
        result = engine.run_case(case)

        assert executed == ["a", "b"]
        assert result.status == CaseStatus.COMPLETED
        assert result.completed_steps == ["framer", "diagnostician"]
    finally:
        os.unlink(db_path)
        os.unlink(ledger_path)


def test_workflow_engine_skips_completed_steps() -> None:
    engine, db_path, ledger_path = _make_engine()
    try:
        executed: list[str] = []

        def step_a(case: Case) -> str:
            executed.append("a")
            return "ok"

        engine.register_step("framer", step_a)

        case = Case(case_id="case-1", title="Test", plan=["framer"])
        case.completed_steps = ["framer"]
        case.status = CaseStatus.COMPLETED
        engine.run_case(case)
        assert executed == []  # jiz hotovo, preskakeno
    finally:
        os.unlink(db_path)
        os.unlink(ledger_path)


def test_workflow_engine_step_failure() -> None:
    engine, db_path, ledger_path = _make_engine()
    try:
        def failing_step(case: Case) -> str:
            raise RuntimeError("chybi data")

        engine.register_step("framer", failing_step)

        case = Case(case_id="case-1", title="Test", plan=["framer"])
        try:
            engine.run_case(case)
            assert False, "mel by vyhodit vyjimku"
        except RuntimeError:
            assert case.status == CaseStatus.FAILED
    finally:
        os.unlink(db_path)
        os.unlink(ledger_path)
