"""Unit testy pro SolutionDesignerAgenta s mocknutým Ollama voláním.

estimated_roi nikdy nepochází z LLM mocku — počítá se deterministicky
pomocí Quant Enginu z dat klienta / explicitních předpokladů.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.solution_designer import (
    SolutionDesignerAgent,
    SolutionDesignerInput,
)
from src.quant.confidence import ConfidenceCalculator, ConfidenceComponents
from src.quant.engine import QuantEngine


@pytest.mark.asyncio
async def test_solution_designer_returns_solutions_and_roi() -> None:
    agent = SolutionDesignerAgent()

    mocked_response = {
        "solutions": [
            {"name": "Automatizace schvalování", "steps": ["Návrh", "Implementace"]},
            {"name": "Outsourcing", "steps": ["Výběr dodavatele", "Smlouva"]},
        ],
        "estimated_roi": 25.0,  # LLM odhad — musí být ignorován ve prospěch Quant Enginu
        "confidence": 0.8,  # LLM sebereflexe — musí být ignorována
    }

    quant_inputs = {
        "investment": 100000,
        "annual_return": 30000,
        "years": 5,
        "discount_rate": 0.08,
    }
    expected_roi = QuantEngine().compute_roi(quant_inputs)["roi"]

    claims = [
        {"id": 1, "text": "Náklady vzrostly o 15 %", "source": "client_data", "evidence": "Procesní analýza"},
    ]
    levels = ["verified"]

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value=mocked_response
    ):
        result = await agent.run(
            SolutionDesignerInput(
                root_causes=["Pomalé schvalování"],
                evidence=["Procesní analýza"],
                claims=claims,
                verification_levels=levels,
                agreement=0.7,
                quant_inputs=quant_inputs,
            )
        )

    assert len(result.solutions) == 2
    # estimated_roi je výsledek Quant Enginu, nikoli mocked hodnota 25.0
    assert result.estimated_roi == expected_roi
    assert result.quant_result is not None
    assert result.quant_result["status"] == "ok"
    expected_confidence = ConfidenceCalculator().score(
        ConfidenceCalculator.from_claims(claims, levels=levels, agreement=0.7)
    )["confidence"]
    assert result.confidence == expected_confidence
    assert result.confidence_basis is not None


@pytest.mark.asyncio
async def test_solution_designer_estimated_roi_is_optional() -> None:
    agent = SolutionDesignerAgent()

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value={
            "solutions": [],
        }
    ):
        result = await agent.run(
            SolutionDesignerInput(root_causes=[], evidence=[])
        )

    assert result.estimated_roi is None
    assert result.solutions == []