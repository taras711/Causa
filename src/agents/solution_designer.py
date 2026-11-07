"""Solution Designer – návrh řešení s kvantifikací."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.agents.base import AutonomyLevel, BaseAgent


class SolutionDesignerInput(BaseModel):
    root_causes: list[str]
    evidence: list[str] = Field(default_factory=list)


class SolutionDesignerOutput(BaseModel):
    solutions: list[dict] = Field(default_factory=list)
    estimated_roi: float | None = None
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class SolutionDesignerAgent(BaseAgent[SolutionDesignerInput, SolutionDesignerOutput]):
    """Navrhuje řešení na základě identifikovaných kořenových příčin.

    Používá velký model pro syntézu řešení. ROI odhad je pouze indikativní;
    přesný výpočet provádí Quant Engine.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="SolutionDesigner",
            autonomy=AutonomyLevel.L1,
            input_schema=SolutionDesignerInput,
            output_schema=SolutionDesignerOutput,
            model_role="large",
            ollama_base_url=kwargs.get(
                "ollama_base_url", "http://localhost:11434"
            ),
        )

    async def run(self, input_data: SolutionDesignerInput) -> SolutionDesignerOutput:
        system_prompt = (
            "Jsi SolutionDesigner agent v platformě Causa. Tvoje role je navrhnout řešení "
            "na základě kořenových příčin a důkazů. Odpovídej vždy v češtině a ve formátu JSON. "
            "Nevytvářej přesné číselné výpočty – ty patří do Quant Enginu. "
            "estimated_roi je pouze orientační odhad v procentech (0–100)."
        )
        causes_text = "\n".join(f"- {c}" for c in input_data.root_causes)
        evidence_text = "\n".join(f"- {e}" for e in input_data.evidence) or "(žádné)"
        user_prompt = (
            f"Kořenové příčiny:\n{causes_text}\n\n"
            f"Důkazy:\n{evidence_text}\n\n"
            "Vrať JSON s klíči: solutions (seznam řešení s popisy a kroky), "
            "estimated_roi (orientační číslo 0–100), confidence (0.0–1.0)."
        )

        result = await self._call_ollama_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=4096,
        )

        return SolutionDesignerOutput(
            solutions=result.get("solutions", []),
            estimated_roi=result.get("estimated_roi"),
            confidence=max(0.0, min(1.0, result.get("confidence", 0.5))),
        )