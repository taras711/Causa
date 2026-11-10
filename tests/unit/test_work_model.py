"""Unit testy pro Pydantic model pracovního modelu firmy (WorkModelBase)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.work_model import WorkModelBase


def test_work_model_base_requires_company_id() -> None:
    wm = WorkModelBase(company_id="firma-abc")
    assert wm.company_id == "firma-abc"
    assert wm.processes == []
    assert wm.roles == []
    assert wm.metrics == {}


def test_work_model_base_custom_fields() -> None:
    wm = WorkModelBase(
        company_id="firma-xyz",
        processes=[{"id": "p1", "name": "Výroba", "owner": "Jan"}],
        roles=[{"id": "r1", "name": "Vedoucí výroby"}],
        metrics={"vyroba_náklady": 1_000_000, "marze": 0.25},
    )
    assert wm.company_id == "firma-xyz"
    assert len(wm.processes) == 1
    assert wm.processes[0]["name"] == "Výroba"
    assert len(wm.roles) == 1
    assert wm.metrics["marze"] == 0.25


def test_work_model_base_company_id_required() -> None:
    with pytest.raises(ValidationError):
        WorkModelBase()  # type: ignore[call-arg]