"""Unit testy pro Pydantic modely předpokladu (AssumptionBase, AssumptionResponse)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from uuid import UUID

from src.models.assumption import AssumptionBase, AssumptionResponse


def test_assumption_base_requires_text_and_value() -> None:
    assumption = AssumptionBase(text="Diskontní sazba", value=0.1)
    assert assumption.text == "Diskontní sazba"
    assert assumption.value == 0.1
    assert assumption.case_id is None
    assert assumption.affected_branches == []


def test_assumption_base_value_types() -> None:
    a_float = AssumptionBase(text="Sazba", value=0.05)
    a_str = AssumptionBase(text="Měna", value="CZK")
    a_bool = AssumptionBase(text="Povoleno", value=True)
    assert a_float.value == 0.05
    assert a_str.value == "CZK"
    assert a_bool.value is True


def test_assumption_base_optional_fields() -> None:
    assumption = AssumptionBase(
        text="Růst trhu",
        value=0.03,
        case_id="case-123",
        affected_branches=["finance", "sales"],
    )
    assert assumption.case_id == "case-123"
    assert assumption.affected_branches == ["finance", "sales"]


def test_assumption_base_text_and_value_required() -> None:
    with pytest.raises(ValidationError):
        AssumptionBase()  # type: ignore[call-arg]


def test_assumption_response_adds_system_fields() -> None:
    assumption = AssumptionBase(text="Sazba", value=0.1)
    response = AssumptionResponse(**assumption.model_dump(exclude_unset=True))
    assert response.assumption_id is not None
    assert isinstance(response.assumption_id, UUID)
    assert response.created_at is not None
    assert response.text == "Sazba"
    assert response.value == 0.1