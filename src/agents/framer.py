"""Framer – definuje rozsah případu a strukturu A3."""
from __future__ import annotations

from pydantic import BaseModel, Field


class FramerInput(BaseModel):
    case_title: str = Field(..., description="Název případu")
    problem_statement: str = Field(..., description="Popis problému klienta")
    context: dict = Field(default_factory=dict)


class FramerOutput(BaseModel):
    scope: str = Field(..., description="Definovaný rozsah případu")
    a3_structure: list[str] = Field(..., description="Struktura A3 analýzy")
    key_questions: list[str] = Field(..., description="Klíčové otázky k vyřešení")