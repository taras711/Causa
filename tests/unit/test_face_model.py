"""Unit testy pro FaceModel schémata."""

from __future__ import annotations

import pytest

from src.models.face_model import (
    FaceModelCreate,
    FaceModelFilter,
    FaceModelList,
    FaceModelResponse,
    FaceModelUpdate,
)


def test_face_model_create_required_fields() -> None:
    fm = FaceModelCreate(
        name="Lean Manufacturing",
        company_context="Střední výrobní firma, automotive",
        mechanism="Eliminace plýtvání (muda) prostřednictvím kontinuálního zlepšování",
    )
    assert fm.name == "Lean Manufacturing"
    assert fm.company_context == "Střední výrobní firma, automotive"
    assert "muda" in fm.mechanism
    assert fm.evidence is None
    assert fm.applicable_to == []
    assert fm.tags == []


def test_face_model_create_optional_fields() -> None:
    fm = FaceModelCreate(
        name="Six Sigma",
        company_context="Velká korporace",
        mechanism="Snížení variability procesů pomocí statistických metod",
        evidence="https://example.com/six-sigma",
        applicable_to=["výroba", "kvalita"],
        tags=["kvalita", "procesy"],
    )
    assert fm.evidence == "https://example.com/six-sigma"
    assert fm.applicable_to == ["výroba", "kvalita"]
    assert fm.tags == ["kvalita", "procesy"]


def test_face_model_response_has_system_fields() -> None:
    fm = FaceModelResponse(
        name="Test Model",
        company_context="Ctx",
        mechanism="Mech",
    )
    assert fm.model_id is not None
    assert fm.curated is False
    assert fm.accuracy_score is None
    assert fm.created_at is not None
    assert fm.updated_at is None


def test_face_model_response_accuracy_bounds() -> None:
    # Platná hodnota
    fm = FaceModelResponse(
        name="Test",
        company_context="Ctx",
        mechanism="Mech",
        accuracy_score=0.85,
    )
    assert fm.accuracy_score == 0.85

    # Hodnota mimo rozsah by měla selhat
    with pytest.raises(ValueError):
        FaceModelResponse(
            name="Test",
            company_context="Ctx",
            mechanism="Mech",
            accuracy_score=1.5,
        )


def test_face_model_update_all_optional() -> None:
    update = FaceModelUpdate()
    assert update.name is None
    assert update.curated is None
    assert update.accuracy_score is None

    update2 = FaceModelUpdate(
        name="Nový název",
        curated=True,
        accuracy_score=0.92,
    )
    assert update2.name == "Nový název"
    assert update2.curated is True
    assert update2.accuracy_score == 0.92


def test_face_model_list_defaults() -> None:
    lst = FaceModelList()
    assert lst.items == []
    assert lst.total == 0

    lst2 = FaceModelList(
        items=[
            FaceModelResponse(name="A", company_context="C", mechanism="M"),
            FaceModelResponse(name="B", company_context="C", mechanism="M"),
        ],
        total=2,
    )
    assert len(lst2.items) == 2
    assert lst2.total == 2


def test_face_model_filter_defaults() -> None:
    f = FaceModelFilter()
    assert f.query is None
    assert f.tags is None
    assert f.curated_only is False
    assert f.min_accuracy is None
    assert f.limit == 20
    assert f.offset == 0


def test_face_model_filter_custom() -> None:
    f = FaceModelFilter(
        query="snížení nákladů",
        tags=["úspory"],
        curated_only=True,
        min_accuracy=0.8,
        limit=10,
        offset=5,
    )
    assert f.query == "snížení nákladů"
    assert f.tags == ["úspory"]
    assert f.curated_only is True
    assert f.min_accuracy == 0.8
    assert f.limit == 10
    assert f.offset == 5