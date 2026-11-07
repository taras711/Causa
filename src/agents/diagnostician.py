"""Diagnostician – A3 logika, analýza příčin."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DiagnosticianInput(BaseModel):
    scope: str
    evidence: list[str] = Field(default_factory=list)


class DiagnosticianOutput(BaseModel):
    root_causes: list[str] = Field(..., description="Identifikované kořenové příčiny")
    contributing_factors: list[str] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0.0, le=1.0)