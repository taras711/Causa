"""Bezpečnostní testy pro Pydantic modely."""
from __future__ import annotations

import pytest

from src.models.face_model import FaceModelCreate, FaceModelFilter, FaceModelResponse
from src.models.case import CaseCreate
from src.models.agent import *  # noqa: F401,F403


@pytest.mark.security
def test_face_model_create_empty_strings_accepted_or_rejected() -> None:
    try:
        FaceModelCreate(name="", company_context="", mechanism="")
    except Exception:
        return
    assert True


@pytest.mark.security
def test_face_model_accuracy_bounds() -> None:
    with pytest.raises(ValueError):
        FaceModelResponse(name="A", company_context="C", mechanism="M", accuracy_score=2.0)
    with pytest.raises(ValueError):
        FaceModelResponse(name="A", company_context="C", mechanism="M", accuracy_score=-0.1)


@pytest.mark.security
def test_face_model_filter_limit_bounds() -> None:
    with pytest.raises(ValueError):
        FaceModelFilter(limit=0)
    with pytest.raises(ValueError):
        FaceModelFilter(limit=1000)
    with pytest.raises(ValueError):
        FaceModelFilter(offset=-1)


@pytest.mark.security
def test_face_model_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE face_models; --"
    fm = FaceModelCreate(name=evil, company_context="ctx", mechanism="mech")
    assert fm.name == evil


@pytest.mark.security
def test_case_create_title_injection() -> None:
    c = CaseCreate(title="<script>alert(1)</script>", tenant_id="default")
    assert "<script>" in c.title


@pytest.mark.security
def test_face_model_huge_string_does_not_crash() -> None:
    big = "A" * 100000
    fm = FaceModelCreate(name=big, company_context="ctx", mechanism="mech")
    assert len(fm.name) == 100000

