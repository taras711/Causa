"""Solution Designer – návrh řešení s kvantifikací přes Quant Engine.

Pravidlo: LLM nevymýšlí čísla. estimated_roi je vypočten deterministicky
Quant Enginem z dat klienta nebo explicitně označených předpokladů.
Confidence je složené, kalibrovatelné skóre z vlastností důkazů,
nikoliv sebereflexe modelu.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.agents.base import AutonomyLevel, BaseAgent
from src.quant.confidence import ConfidenceCalculator
from src.quant.engine import QuantEngine


class SolutionDesignerInput(BaseModel):
    root_causes: list[str]
    evidence: list[str] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)
    # Claimy ze Case se zdroji (work_model | client_data | face_model | assumption).
    claims: list[dict] = Field(default_factory=list)
    # Verifikační úrovně odpovídající claimům (verified | partial | unverified).
    verification_levels: list[str] = Field(default_factory=list)
    # Shoda napříč během / modely pro stejné tvrzení [0, 1].
    agreement: float = Field(0.0, ge=0.0, le=1.0)
    # Vstupy pro deterministický Quant Engine (investice, roční návratnost, ...).
    quant_inputs: dict | None = None


class SolutionDesignerOutput(BaseModel):
    solutions: list[dict] = Field(default_factory=list)
    estimated_roi: float | None = None
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    quant_result: dict | None = None
    confidence_basis: dict | None = None


class SolutionDesignerAgent(BaseAgent[SolutionDesignerInput, SolutionDesignerOutput]):
    """Navrhuje řešení na základě identifikovaných kořenových příčin.

    Používá velký model pro syntézu řešení. Přesné číslo ROI počítá Quant Engine;
    LLM jen navrhuje strukturu řešení. Confidence je deterministický součet
    vlastností důkazů, nikoliv LLM sebereflexe.
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
        self._engine = QuantEngine()
        self._confidence = ConfidenceCalculator()

    async def run(self, input_data: SolutionDesignerInput) -> SolutionDesignerOutput:
        system_prompt = (
            "Jsi SolutionDesigner agent v platformě Causa. Tvoje role je navrhnout řešení "
            "na základě kořenových příčin a důkazů. Odpovídej vždy v češtině a ve formátu JSON. "
            "Nevytvářej přesné číselné výpočty – ty patří do Quant Enginu. "
            "estimated_roi je počítáno deterministicky z dat klienta nebo explicitních předpokladů."
        )
        causes_text = "\n".join(f"- {c}" for c in input_data.root_causes)
        evidence_text = "\n".join(f"- {e}" for e in input_data.evidence) or "(žádné)"
        context_text = "\n".join(
            f"- {key}: {value}" for key, value in input_data.context.items()
            if key not in {"framing", "evidence", "diagnosis", "solution"} and value
        ) or "(další kontext neuveden)"
        quant_hint = ""
        if input_data.quant_inputs:
            quant_hint = (
                f"\nVstupy pro Quant Engine (spočítá se deterministicky): "
                f"{input_data.quant_inputs}"
            )
        user_prompt = (
            f"Kořenové příčiny:\n{causes_text}\n\n"
            f"Kontext případu:\n{context_text}\n\n"
            f"Důkazy:\n{evidence_text}{quant_hint}\n\n"
            "Vrať JSON s klíči: solutions (seznam řešení s popisy a kroky). "
            "Číselné odhady nevytvářejte."
        )

        result = await self._call_ollama_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=4096,
        )

        # Deterministický výpočet ROI přes Quant Engine (nikdy LLM-generated).
        quant_result = None
        estimated_roi = None
        if isinstance(input_data.quant_inputs, dict):
            quant_result = self._engine.compute_roi(input_data.quant_inputs)
            estimated_roi = quant_result.get("roi")

        # Složené confidence z vlastností důkazů (nikoliv LLM sebereflexe).
        components = ConfidenceCalculator.from_claims(
            claims=input_data.claims,
            levels=input_data.verification_levels,
            agreement=input_data.agreement,
        )
        scored = self._confidence.score(components)

        return SolutionDesignerOutput(
            solutions=result.get("solutions", []),
            estimated_roi=estimated_roi,
            confidence=round(scored["confidence"], 4),
            quant_result=quant_result,
            confidence_basis={
                "components": scored["components"],
                "weights": scored["weights"],
                "calibrated": scored["calibrated"],
            },
        )