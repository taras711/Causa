"""Unit testy pro core/case.py — Case model, claimy, doporučení."""

from __future__ import annotations

from src.core.case import Case, CaseStatus, CaseStep


def test_case_creation_defaults() -> None:
    case = Case(case_id="case-1", title="Testovací případ")
    assert case.case_id == "case-1"
    assert case.title == "Testovací případ"
    assert case.tenant_id == "default"
    assert case.status == CaseStatus.DRAFT
    assert case.plan == []
    assert case.claims == []
    assert case.recommendations == []


def test_case_add_claim() -> None:
    case = Case(case_id="case-1", title="Test")
    claim = case.add_claim(
        text="70 % uživatelů odchází po 30 dnech",
        source="client_data",
        evidence="analytics export",
        confidence=0.85,
    )
    assert claim["id"] == 1
    assert claim["text"] == "70 % uživatelů odchází po 30 dnech"
    assert claim["source"] == "client_data"
    assert claim["evidence"] == "analytics export"
    assert claim["confidence"] == 0.85
    assert claim["verified"] is False
    assert "created_at" in claim

    claim2 = case.add_claim(text="druhé tvrzení", source="assumption", assumption=True)
    assert claim2["id"] == 2
    assert claim2["assumption"] is True


def test_case_add_recommendation() -> None:
    case = Case(case_id="case-1", title="Test")
    case.add_claim(text="claim A", source="client_data", confidence=0.9)
    rec = case.add_recommendation(
        text="Přepracovat navigaci",
        basis_claim_ids=[1],
        roi=25.0,
        confidence=0.8,
    )
    assert rec["id"] == 1
    assert rec["text"] == "Přepracovat navigaci"
    assert rec["basis_claim_ids"] == [1]
    assert rec["roi"] == 25.0
    assert rec["confidence"] == 0.8


def test_case_status_enum_values() -> None:
    assert CaseStatus.DRAFT.value == "draft"
    assert CaseStatus.RUNNING.value == "running"
    assert CaseStatus.COMPLETED.value == "completed"
    assert CaseStatus.FAILED.value == "failed"
    assert CaseStatus.PAUSED.value == "paused"


def test_case_step_fields() -> None:
    step = CaseStep(step_name="framer", status="running")
    assert step.step_name == "framer"
    assert step.status == "running"
    assert step.result is None
    assert step.error is None
