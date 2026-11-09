"""FaceModel schéma - anonymizovaný vzor uspesneho business cases."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FaceModelContext(BaseModel):
    """Kontext FaceModelu - odvětví, velikost firmy, role atd."""

    industry: str
    company_size: str
    employee_role: str
    problem_area: str
    timeline: str
    region: str | None = None


class FaceModelProblem(BaseModel):
    """Definice problému ve FaceModelu."""

    title: str
    description: str
    symptoms: list[str] = Field(default_factory=list)
    impact_description: str | None = None


class FaceModelRootCause(BaseModel):
    """Identifikovaná kořenová příčina s důkazem."""

    cause: str
    evidence: str | None = None
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class FaceModelSolution(BaseModel):
    """Navrhované řešení s odhadovaným dopadem."""

    title: str
    description: str
    steps: list[str] = Field(default_factory=list)
    estimated_roi: float | None = None
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    basis_claim_ids: list[int] = Field(default_factory=list)


class FaceModelResult(BaseModel):
    """Dosáhnuté výsledky po implementaci."""

    achieved_roi: float | None = None
    achieved_npv: float | None = None
    metrics_improved: list[str] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)


class FaceModel(BaseModel):
    """Anonymizovaný vzor uspesneho business cases pro inspiraci a verifikaci.

    FaceModel je kurátorský záznam v znalostní bázi, který slouží jako
    reference pro podobné business případy. Obsahuje kontext, problém,
    kořenové příčiny, řešení, dosažené výsledky a podmínky přenositelnosti.
    """

    face_model_id: UUID = Field(default_factory=uuid4)
    title: str
    context: FaceModelContext
    problem: FaceModelProblem
    root_causes: list[FaceModelRootCause] = Field(default_factory=list)
    solutions: list[FaceModelSolution] = Field(default_factory=list)
    result: FaceModelResult | None = None
    source: str  # původ dat (interní, publikováno, atd.)
    license: str | None = None  # autorské práva / licence k použití
    transferability_conditions: list[str] = Field(
        default_factory=list,
        description="Podmínky za kterých lze FaceModel přenést do jiného kontextu",
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class FaceModelCreate(BaseModel):
    """Vstupní schéma pro vytvoření nového FaceModelu."""

    title: str
    context: dict[str, Any]
    problem: dict[str, Any]
    root_causes: list[dict[str, Any]] = Field(default_factory=list)
    solutions: list[dict[str, Any]] = Field(default_factory=list)
    source: str
    license: str | None = None
    transferability_conditions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class FaceModelResponse(FaceModelCreate):
    """Výstupní schéma s ID a časovými razítky."""

    face_model_id: UUID
    created_at: datetime
    updated_at: datetime
