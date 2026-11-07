"""Verifier – ověření tvrzení proti důkazům, datům klienta nebo předpokladům."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.agents.base import AutonomyLevel, BaseAgent


class VerifierInput(BaseModel):
    claim_text: str
    source: str  # work_model | client_data | assumption
    evidence: str | None = None


class VerifierOutput(BaseModel):
    verified: bool
    verification_level: str = Field(..., description="unverified | partial | verified")
    notes: str = ""


class VerifierAgent(BaseAgent[VerifierInput, VerifierOutput]):
    """Ověřuje tvrzení proti WorkModelu, datům klienta nebo explicitně označeným předpokladům.

    Každé tvrzení musí mít stopu původu. Verifikace je dokumentována v ledgeru.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="Verifier",
            autonomy=AutonomyLevel.L2,
            input_schema=VerifierInput,
            output_schema=VerifierOutput,
            model_name=kwargs.get("model_name", "qwen2.5:14b"),
            ollama_base_url=kwargs.get(
                "ollama_base_url", "http://localhost:11434"
            ),
        )

    async def run(self, input_data: VerifierInput) -> VerifierOutput:
        system_prompt = (
            "Jsi Verifier agent v platformě Causa. Tvoje role je ověřit tvrzení proti "
            "dostupným důkazům, WorkModelu nebo předpokladům. Odpovídej vždy v češtině "
            "a ve formátu JSON. verification_level může být: unverified, partial, verified."
        )
        evidence_text = input_data.evidence or "(žádné dodatečné důkazy)"
        user_prompt = (
            f"Tvrzení: {input_data.claim_text}\n"
            f"Zdroj: {input_data.source}\n"
            f"Důkazy: {evidence_text}\n\n"
            "Vrať JSON s klíči: verified (true/false), verification_level "
            "(unverified | partial | verified), notes (odůvodnění)."
        )

        result = await self._call_ollama_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=2048,
        )

        level = result.get("verification_level", "unverified")
        if level not in ("unverified", "partial", "verified"):
            level = "unverified"

        return VerifierOutput(
            verified=result.get("verified", False),
            verification_level=level,
            notes=result.get("notes", ""),
        )