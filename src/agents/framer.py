"""Framer – definuje rozsah případu a strukturu A3."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.agents.base import AutonomyLevel, BaseAgent


class FramerInput(BaseModel):
    case_title: str = Field(..., description="Název případu")
    problem_statement: str = Field(..., description="Popis problému klienta")
    context: dict = Field(default_factory=dict)


class FramerOutput(BaseModel):
    scope: str = Field(..., description="Definovaný rozsah případu")
    a3_structure: list[str] = Field(..., description="Struktura A3 analýzy")
    key_questions: list[str] = Field(..., description="Klíčové otázky k vyřešení")


class FramerAgent(BaseAgent[FramerInput, FramerOutput]):
    """Definuje rozsah případu a navrhuje strukturu A3 analýzy.

    Používá malý model (qwen2.5:3b) pro klasifikaci a extrakci.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="Framer",
            autonomy=AutonomyLevel.L1,
            input_schema=FramerInput,
            output_schema=FramerOutput,
            model_name=kwargs.get("model_name", "qwen2.5:3b"),
            ollama_base_url=kwargs.get(
                "ollama_base_url", "http://localhost:11434"
            ),
        )

    async def run(self, input_data: FramerInput) -> FramerOutput:
        system_prompt = (
            "Jsi Framer agent v platformě Causa. Tvoje role je definovat rozsah případu "
            "a navrhnout strukturu A3 analýzy. Odpovídej vždy v češtině a ve formátu JSON. "
            "Nevytvářej číselné odhady – ty pertenece Quant Enginu."
        )
        user_prompt = (
            f"Název případu: {input_data.case_title}\n"
            f"Popis problému: {input_data.problem_statement}\n"
            f"Kontext: {input_data.context}\n\n"
            "Vrať JSON s klíči: scope, a3_structure (seznam fází A3), key_questions (seznam otázek)."
        )

        result = await self._call_ollama_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=2048,
        )

        return FramerOutput(
            scope=result.get("scope", input_data.problem_statement[:200]),
            a3_structure=result.get(
                "a3_structure",
                ["Pozadí", "Současný stav", "Kořenové příčiny", "Řešení", "Plán"],
            ),
            key_questions=result.get("key_questions", []),
        )