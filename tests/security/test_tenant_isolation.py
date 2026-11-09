"""Bezpečnostní testy izolace tenantů a oddělení případů."""

from __future__ import annotations

import sqlite3
import tempfile

import pytest

from src.core.case import Case, CaseStatus
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


class TestTenantIsolation:
    """Případy s různými tenant_id musí zůstat izolované."""

    def test_ledger_returns_only_records_for_given_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(f"{tmp}/ledger.db")
            ledger.append("step_completed", case_id="case-tenant-a", step="framer")
            ledger.append("step_completed", case_id="case-tenant-a", step="diagnostician")
            ledger.append("step_completed", case_id="case-tenant-b", step="framer")

            records_a = ledger.get_for_case("case-tenant-a")
            records_b = ledger.get_for_case("case-tenant-b")

            assert len(records_a) == 2
            assert all(r["case_id"] == "case-tenant-a" for r in records_a)
            assert len(records_b) == 1
            assert records_b[0]["case_id"] == "case-tenant-b"

    def test_ledger_returns_empty_for_unknown_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(f"{tmp}/ledger.db")
            records = ledger.get_for_case("nonexistent-case")
            assert records == []

    def test_cases_with_different_tenants_remain_separate(self) -> None:
        case_a = Case(
            case_id="case-a",
            title="Případ A",
            tenant_id="tenant-acme",
            plan=["framer", "diagnostician"],
        )
        case_b = Case(
            case_id="case-b",
            title="Případ B",
            tenant_id="tenant-cognit",
            plan=["framer", "diagnostician"],
        )
        assert case_a.tenant_id != case_b.tenant_id
        assert case_a.case_id != case_b.case_id

    def test_case_status_transition_is_per_case(self) -> None:
        case = Case(case_id="case-x", title="X", tenant_id="tenant-acme")
        assert case.status == CaseStatus.DRAFT
        case.status = CaseStatus.RUNNING
        assert case.status == CaseStatus.RUNNING

        # Jiný případ není ovlivněn
        other = Case(case_id="case-y", title="Y", tenant_id="tenant-cognit")
        assert other.status == CaseStatus.DRAFT

    def test_engine_persists_case_per_case_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = f"{tmp}/engine.db"
            # Vytvorit tabulku cases, kterou WorkflowEngine pouziva k persistenci
            conn = sqlite3.connect(db_path)
            conn.execute(_CASES_DDL)
            conn.commit()
            conn.close()
            ledger = Ledger(f"{tmp}/ledger.db")
            engine = WorkflowEngine(db_path, ledger)

            case = Case(
                case_id="case-1",
                title="První",
                tenant_id="tenant-acme",
                plan=["step-1"],
            )

            def step_1(case: Case) -> str:
                return "done"

            engine.register_step("step-1", step_1)
            result = engine.run_case(case)

            assert result.status == CaseStatus.COMPLETED
            assert result.completed_steps == ["step-1"]

            # Ledger obsahuje záznamy pouze pro tento případ
            records = ledger.get_for_case("case-1")
            assert len(records) >= 2  # step_started + step_completed
            assert all(r["case_id"] == "case-1" for r in records)
