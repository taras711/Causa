"""Unit testy pro Pydantic modely tvrzení (ClaimBase, ClaimCreate, ClaimResponse)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from uuid import UUID

from src.models.claim import ClaimBase, ClaimCreate, ClaimResponse


def test_claim_base_requires_text_and_source() -> None:
    claim = ClaimBase(text="Výnos klesl o 10 %", source="client_data")
    assert claim.text == "Výnos klesl o 10 %"
    assert claim.source == "client_data"
    assert claim.evidence is None
    assert claim.assumption is False
    assert claim.confidence is None


def test_claim_base_optional_fields() -> None:
    claim = ClaimBase(
        text="Náklady vzrostly",
        source="work_model",
        evidence="Finanční výkaz 2024",
        assumption=True,
        confidence=0.85,
    )
    assert claim.evidence == "Finanční výkaz 2024"
    assert claim.assumption is True
    assert claim.confidence == 0.85


def test_claim_confidence_must_be_between_0_and_1() -> None:
    with pytest.raises(ValidationError):
        ClaimBase(text="T", source="s", confidence=1.5)
    with pytest.raises(ValidationError):
        ClaimBase(text="T", source="s", confidence=-0.1)


def test_claim_create_requires_case_id() -> None:
    import uuid

    case_id = uuid.uuid4()
    create = ClaimCreate(text="T", source="s", case_id=case_id)
    assert create.case_id == case_id


def test_claim_create_case_id_is_required() -> None:
    with pytest.raises(ValidationError):
        ClaimCreate(text="T", source="s")  # type: ignore[call-arg]


def test_claim_response_adds_system_fields() -> None:
    import uuid

    case_id = uuid.uuid4()
    create = ClaimCreate(text="T", source="s", case_id=case_id)
    response = ClaimResponse(**create.model_dump(exclude_unset=True))
    assert response.claim_id is not None
    assert isinstance(response.claim_id, UUID)
    assert response.case_id == case_id
    assert response.verified is False
    assert response.created_at is not None
    assert response.text == "T"