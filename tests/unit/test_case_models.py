"""Unit testy pro Pydantic modely případu (CaseBase, CaseCreate, CaseResponse)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from uuid import UUID

from src.models.case import CaseBase, CaseCreate, CaseResponse


def test_case_create_requires_title() -> None:
    create = CaseCreate(title="Nákladové úspory")
    assert create.title == "Nákladové úspory"
    assert create.tenant_id == "default"
    assert create.context == {}
    assert create.plan == []


def test_case_create_custom_fields() -> None:
    create = CaseCreate(
        title="Zlepšení dodací lhůty",
        tenant_id="tenant-acme",
        context={"problem": "SLA překročen o 5 dnů"},
        plan=["framer", "diagnostician", "solution_designer"],
    )
    assert create.title == "Zlepšení dodací lhůty"
    assert create.tenant_id == "tenant-acme"
    assert create.context == {"problem": "SLA překročen o 5 dnů"}
    assert create.plan == ["framer", "diagnostician", "solution_designer"]


def test_case_create_title_is_required() -> None:
    with pytest.raises(ValidationError):
        CaseCreate()  # type: ignore[call-arg]


def test_case_response_adds_system_fields() -> None:
    create = CaseCreate(title="Test", tenant_id="default")
    response = CaseResponse(**create.model_dump(exclude_unset=True))
    assert response.case_id is not None
    assert isinstance(response.case_id, UUID)
    assert response.status == "draft"
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.title == "Test"
    assert response.tenant_id == "default"


def test_case_response_custom_status() -> None:
    response = CaseResponse(
        title="Test",
        status="running",
    )
    assert response.status == "running"