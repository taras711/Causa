"""Unit testy pro DiagnosticianAgenta s mocknutým Ollama voláním.

Confidence není sebereflexe LLM, ale deterministické složené skóre
z vlastností důkazů (ConfidenceCalculator).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.diagnostician import DiagnosticianAgent, DiagnosticianInput
from src.quant.confidence import ConfidenceCalculator, ConfidenceComponents


@pytest.mark.asyncio
async def test_diagnostician_run_returns_root_causes() -> None:
    agent = DiagnosticianAgent()

    mocked_response = {
        "root_causes": ["Neefektivní proces", "Nedostatek dat"],
        "contributing_factors": ["Lidská chyba"],
        "confidence": 0.9,  # LLM hodnota je ignorována; confidence se počítá deterministicky
    }

    claims = [
        {"id": 1, "text": "Náklady vzrostly o 15 %", "source": "client_data", "evidence": "Výkaz zisků 2024"},
        {"id": 2, "text": "Příčina je v procesu", "source": "work_model"},
    ]
    levels = ["verified", "verified"]

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value=mocked_response
    ):
        result = await agent.run(
            DiagnosticianInput(
                scope="Optimalizace nákladů",
                evidence=["Výkaz zisků 2024"],
                claims=claims,
                verification_levels=levels,
                agreement=0.8,
            )
        )

    assert result.root_causes == ["Neefektivní proces", "Nedostatek dat"]
    assert result.contributing_factors == ["Lidská chyba"]
    expected = ConfidenceCalculator().score(
        ConfidenceCalculator.from_claims(claims, levels=levels, agreement=0.8)
    )["confidence"]
    assert result.confidence == expected
    assert result.confidence_basis is not None
    assert result.confidence_basis["calibrated"] is False


@pytest.mark.asyncio
async def test_diagnostician_handles_missing_evidence() -> None:
    agent = DiagnosticianAgent()

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value={
            "root_causes": [],
            "contributing_factors": [],
            "confidence": 0.5,
        }
    ):
        result = await agent.run(
            DiagnosticianInput(scope="Test", evidence=[])
        )

    assert result.root_causes == []
    # Bez claimů je confidence deterministicky 0.0 (žádné důkazy k posouzení).
    assert result.confidence == 0.0
    assert result.confidence_basis["components"]["source_quality"] == 0.0