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


class FaceModelBase(BaseModel):
    """Základní pole FaceModelu (bez systémových polí)."""

    name: str
    company_context: str
    mechanism: str
    evidence: str | None = None
    applicable_to: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    curated: bool | None = None
    accuracy_score: float | None = Field(None, ge=0.0, le=1.0)


class FaceModelCreate(FaceModelBase):
    """Data pro vytvoření nového FaceModel záznamu (bez systémových polí)."""


class FaceModelResponse(FaceModelBase):
    """Výstupní schéma s ID a časovými razítky."""

    model_id: UUID = Field(default_factory=uuid4)
    curated: bool = False
    accuracy_score: float | None = Field(None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None


class FaceModelFilter(BaseModel):
    """Filtry pro vyhledávání v FaceModel knowledge base."""

    query: str | None = Field(None, description="Fulltextový dotaz nad názvem, mechanismem a tagy")
    tags: list[str] | None = Field(None, description="Povinné tagy (průnik)")
    applicable_to: list[str] | None = Field(None, description="Použitelnost pro dané kontexty")
    curated_only: bool = Field(False, description="Pouze kurátorsky schválené záznamy")
    min_accuracy: float | None = Field(None, ge=0.0, le=1.0, description="Minimální accuracy skóre")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class FaceModelList(BaseModel):
    """Výpis FaceModel záznamů s celkovým počtem pro stránkování."""

    items: list[FaceModelResponse] = Field(default_factory=list)
    total: int = 0


class FaceModelUpdate(BaseModel):
    """Volitelné aktualizační pole pro existující FaceModel záznam."""

    name: str | None = None
    company_context: str | None = None
    mechanism: str | None = None
    evidence: str | None = None
    applicable_to: list[str] | None = None
    tags: list[str] | None = None
    curated: bool | None = None
    accuracy_score: float | None = Field(None, ge=0.0, le=1.0)
