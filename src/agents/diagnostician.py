"""Diagnostician – A3 logika, analýza příčin."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.agents.base import AutonomyLevel, BaseAgent


class DiagnosticianInput(BaseModel):
    scope: str
    evidence: list[str] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)


class DiagnosticianOutput(BaseModel):
    root_causes: list[str] = Field(..., description="Identifikované kořenové příčiny")
    contributing_factors: list[str] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class DiagnosticianAgent(BaseAgent[DiagnosticianInput, DiagnosticianOutput]):
    """Analýza příčin (root cause analysis) pro definovaný rozsah případu.

    Používá velký model (qwen3:14b) pro uvažování a syntézu.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="Diagnostician",
            autonomy=AutonomyLevel.L1,
            input_schema=DiagnosticianInput,
            output_schema=DiagnosticianOutput,
            model_role="large",
            ollama_base_url=kwargs.get(
                "ollama_base_url", "http://localhost:11434"
            ),
        )

    async def run(self, input_data: DiagnosticianInput) -> DiagnosticianOutput:
        system_prompt = (
            "Jsi Diagnostician agent v platformě Causa. Tvoje role je identifikovat "
            "kořenové příčiny problémů na základě rozsahu případu a dostupných důkazů. "
            "Odpovídej vždy v češtině a ve formátu JSON. Nevytvářej číselné odhady."
        )
        evidence_text = "\n".join(f"- {e}" for e in input_data.evidence) or "(žádné důkazy)"
        context_text = "\n".join(
            f"- {key}: {value}" for key, value in input_data.context.items()
            if key not in {"framing", "evidence", "diagnosis", "solution"} and value
        ) or "(další kontext neuveden)"
        user_prompt = (
            f"Rozsah případu: {input_data.scope}\n"
            f"Kontext případu:\n{context_text}\n\n"
            f"Dostupné důkazy:\n{evidence_text}\n\n"
            "Vrať JSON s klíči: root_causes (seznam kořenových příčin), "
            "contributing_factors (seznam přispívajících faktorů), confidence (0.0–1.0)."
        )

        result = await self._call_ollama_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=4096,
        )

        return DiagnosticianOutput(
            root_causes=result.get("root_causes", []),
            contributing_factors=result.get("contributing_factors", []),
            confidence=max(0.0, min(1.0, result.get("confidence", 0.5))),
        )