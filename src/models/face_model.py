"""FaceModel – ověřený vzor firemního rozhodování s kontextem a mechanismem úspěchu."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FaceModelBase(BaseModel):
    name: str
    company_context: str = Field(..., description="Kontext firmy (velikost, odvětví atd.)")
    mechanism: str = Field(..., description="Mechanismus úspěchu")
    evidence: str | None = Field(None, description="Odkaz na zdroj/důkaz")
    applicable_to: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class FaceModelCreate(FaceModelBase):
    """Data pro vytvoření nového FaceModel záznamu (bez systémových polí)."""


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


class FaceModelResponse(FaceModelBase):
    model_id: UUID = Field(default_factory=uuid4)
    curated: bool = False
    accuracy_score: float | None = Field(None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None


class FaceModelList(BaseModel):
    """Výpis FaceModel záznamů s celkovým počtem pro stránkování."""

    items: list[FaceModelResponse] = Field(default_factory=list)
    total: int = 0


class FaceModelFilter(BaseModel):
    """Filtry pro vyhledávání v FaceModel knowledge base."""

    query: str | None = Field(None, description="Fulltextový dotaz nad názvem, mechanismem a tagy")
    tags: list[str] | None = Field(None, description="Povinné tagy (průnik)")
    applicable_to: list[str] | None = Field(None, description="Použitelnost pro dané kontexty")
    curated_only: bool = Field(False, description="Pouze kurátorsky schválené záznamy")
    min_accuracy: float | None = Field(None, ge=0.0, le=1.0, description="Minimální accuracy skóre")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)