"""Solution Designer – návrh řešení s kvantifikací."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SolutionDesignerInput(BaseModel):
    root_causes: list[str]
    evidence: list[str] = Field(default_factory=list)


class SolutionDesignerOutput(BaseModel):
    solutions: list[dict] = Field(default_factory=list)
    estimated_roi: float | None = None
    confidence: float = Field(0.5, ge=0.0, le=1.0)