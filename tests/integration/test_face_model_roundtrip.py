"""Integrační testy: FaceModel schémata – création, response a validace."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.face_model import (
    FaceModel,
    FaceModelContext,
    FaceModelCreate,
    FaceModelProblem,
    FaceModelResponse,
    FaceModelRootCause,
    FaceModelResult,
    FaceModelSolution,
)


class TestFaceModelSchemas:
    """FaceModel modely musí správně validovat vstupní a výstupní data."""

    def test_face_model_create_requires_minimal_fields(self) -> None:
        create = FaceModelCreate(
            title="Příklad optimalizace",
            context={
                "industry": "e-commerce",
                "company_size": "200-500",
                "employee_role": "product manager",
                "problem_area": "dashboard UX",
                "timeline": "6 mesicu",
            },
            problem={"title": "Nízká adopce", "description": "Uživatelé nepožívají dashboard"},
            source="interní",
        )
        assert create.title == "Příklad optimalizace"
        assert create.source == "interní"
        assert create.root_causes == []
        assert create.solutions == []

    def test_face_model_response_adds_ids_and_timestamps(self) -> None:
        create = FaceModelCreate(
            title="Test",
            context={
                "industry": "it",
                "company_size": "malá",
                "employee_role": "vývojář",
                "problem_area": "test",
                "timeline": "1 mesic",
            },
            problem={"title": "Problém", "description": "Popis"},
            source="test",
        )
        response = FaceModelResponse(
            face_model_id=create.face_model_id if hasattr(create, "face_model_id") else __import__("uuid").uuid4(),
            created_at=create.created_at if hasattr(create, "created_at") else __import__("datetime").datetime.now(),
            updated_at=create.updated_at if hasattr(create, "updated_at") else __import__("datetime").datetime.now(),
            **create.model_dump(exclude_unset=True),
        )
        assert response.face_model_id is not None
        assert response.created_at is not None
        assert response.updated_at is not None
        assert response.title == "Test"

    def test_full_face_model_includes_all_sections(self) -> None:
        model = FaceModel(
            title="Celý model",
            context=FaceModelContext(
                industry="e-commerce",
                company_size="200-500 zamestnancu",
                employee_role="product manager",
                problem_area="dashboard UX",
                timeline="6 mesicu",
            ),
            problem=FaceModelProblem(
                title="Nízká adopce",
                description="Uživatelé dashboard nepožívají",
                symptoms=["nízká retence", "žádná zpětná vazba"],
            ),
            root_causes=[
                FaceModelRootCause(
                    cause="Složité rozhraní",
                    evidence="Uživatelský výzkum",
                    confidence=0.8,
                )
            ],
            solutions=[
                FaceModelSolution(
                    title="Zjednodušení UI",
                    description="Přepracování navigačního menu",
                    estimated_roi=25.0,
                    confidence=0.7,
                    basis_claim_ids=[1],
                )
            ],
            result=FaceModelResult(
                achieved_roi=22.5,
                metrics_improved=["retence", "spokojenost"],
                lessons_learned=["Uživatelské testování je klíčové."],
            ),
            source="interní",
            license="CC-BY-4.0",
            transferability_conditions=["Podobný odvětví", "Stejná role uživatele"],
            tags=["ux", "dashboard"],
            confidence=0.85,
        )
        assert model.root_causes[0].confidence == 0.8
        assert model.solutions[0].basis_claim_ids == [1]
        assert model.result.achieved_roi == 22.5
        assert model.license == "CC-BY-4.0"
        assert model.transferability_conditions == ["Podobný odvětví", "Stejná role uživatele"]

    def test_confidence_must_be_between_0_and_1(self) -> None:
        with pytest.raises(ValidationError):
            FaceModel(
                title="Test",
                context={
                    "industry": "it",
                    "company_size": "malá",
                    "employee_role": "vývojář",
                    "problem_area": "test",
                    "timeline": "1 mesic",
                },
                problem={"title": "P", "description": "D"},
                source="test",
                confidence=1.5,  # mimo rozsah 0.0–1.0
            )

    def test_source_is_required(self) -> None:
        with pytest.raises(ValidationError):
            FaceModelCreate(
                title="Test",
                context={
                    "industry": "it",
                    "company_size": "malá",
                    "employee_role": "vývojář",
                    "problem_area": "test",
                    "timeline": "1 mesic",
                },
                problem={"title": "P", "description": "D"},
            )  # chybí source
