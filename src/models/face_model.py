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


class FaceModelResponse(FaceModelBase):
    model_id: UUID = Field(default_factory=uuid4)
    curated: bool = False
    accuracy_score: float | None = Field(None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)