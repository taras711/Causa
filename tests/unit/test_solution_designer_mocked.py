"""Unit testy pro SolutionDesignerAgenta s mocknutým Ollama voláním."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.solution_designer import (
    SolutionDesignerAgent,
    SolutionDesignerInput,
)


@pytest.mark.asyncio
async def test_solution_designer_returns_solutions_and_roi() -> None:
    agent = SolutionDesignerAgent()

    mocked_response = {
        "solutions": [
            {"name": "Automatizace schvalování", "steps": ["Návrh", "Implementace"]},
            {"name": "Outsourcing", "steps": ["Výběr dodavatele", "Smlouva"]},
        ],
        "estimated_roi": 25.0,
        "confidence": 0.8,
    }

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value=mocked_response
    ):
        result = await agent.run(
            SolutionDesignerInput(
                root_causes=["Pomalé schvalování"],
                evidence=["Procesní analýza"],
            )
        )

    assert len(result.solutions) == 2
    assert result.estimated_roi == 25.0
    assert result.confidence == 0.8


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