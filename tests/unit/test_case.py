"""Unit testy pro model případu (Case, CaseStatus, CaseStep)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.core.case import Case, CaseStatus, CaseStep


def test_case_initial_status_is_draft() -> None:
    case = Case(case_id="case-1", title="Testovací případ")
    assert case.case_id == "case-1"
    assert case.title == "Testovací případ"
    assert case.status == CaseStatus.DRAFT
    assert case.plan == []
    assert case.completed_steps == []
    assert case.claims == []
    assert case.recommendations == []
    assert isinstance(case.created_at, datetime)
    assert case.created_at.tzinfo is not None


def test_case_step_defaults() -> None:
    step = CaseStep(step_name="framer")
    assert step.step_name == "framer"
    assert step.status == "pending"
    assert step.started_at is None
    assert step.completed_at is None
    assert step.result is None
    assert step.error is None


def test_add_claim_returns_dict_with_required_fields() -> None:
    case = Case(case_id="case-1", title="Test")
    claim = case.add_claim(
        text="Výnos klesl o 10 %",
        source="client_data",
        evidence="Finanční výkaz 2024",
        assumption=False,
        confidence=0.9,
    )
    assert claim["id"] == 1
    assert claim["text"] == "Výnos klesl o 10 %"
    assert claim["source"] == "client_data"
    assert claim["evidence"] == "Finanční výkaz 2024"
    assert claim["assumption"] is False
    assert claim["confidence"] == 0.9
    assert claim["verified"] is False
    assert "created_at" in claim


def test_add_claim_increments_id() -> None:
    case = Case(case_id="case-1", title="Test")
    case.add_claim(text="Claim A", source="work_model")
    case.add_claim(text="Claim B", source="assumption", assumption=True)
    assert len(case.claims) == 2
    assert case.claims[0]["id"] == 1
    assert case.claims[1]["id"] == 2


def test_add_recommendation_returns_dict_with_required_fields() -> None:
    case = Case(case_id="case-1", title="Test")
    case.add_claim(text="Základní tvrzení", source="client_data")
    rec = case.add_recommendation(
        text="Zavést nový proces",
        basis_claim_ids=[1],
        roi=15.5,
        confidence=0.8,
    )
    assert rec["id"] == 1
    assert rec["text"] == "Zavést nový proces"
    assert rec["basis_claim_ids"] == [1]
    assert rec["roi"] == 15.5
    assert rec["confidence"] == 0.8
    assert "created_at" in rec


def test_case_status_enum_values() -> None:
    assert CaseStatus.DRAFT == "draft"
    assert CaseStatus.RUNNING == "running"
    assert CaseStatus.COMPLETED == "completed"
    assert CaseStatus.FAILED == "failed"
    assert CaseStatus.PAUSED == "paused"


def test_case_tenant_defaults_to_default() -> None:
    case = Case(case_id="case-1", title="Test")
    assert case.tenant_id == "default"


def test_case_custom_tenant() -> None:
    case = Case(case_id="case-1", title="Test", tenant_id="tenant-acme")
    assert case.tenant_id == "tenant-acme"