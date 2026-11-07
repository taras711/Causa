"""Unit testy pro FramerAgenta s mocknutým Ollama voláním."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.framer import FramerAgent, FramerInput, FramerOutput


@pytest.mark.asyncio
async def test_framer_run_returns_validated_output() -> None:
    agent = FramerAgent()

    mocked_response = {
        "scope": "Optimalizace nákladů",
        "a3_structure": ["Pozadí", "Současný stav", "Kořenové příčiny", "Řešení", "Plán"],
        "key_questions": ["Jak snížit náklady?", "Kdo je zodpovědný?"],
    }

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value=mocked_response
    ):
        result = await agent.run(
            FramerInput(
                case_title="Nákladové úspory",
                problem_statement="Vysoké režijní náklady v provozu",
            )
        )

    assert isinstance(result, FramerOutput)
    assert result.scope == "Optimalizace nákladů"
    assert len(result.a3_structure) == 5
    assert len(result.key_questions) == 2


@pytest.mark.asyncio
async def test_framer_uses_defaults_when_ollama_returns_partial() -> None:
    agent = FramerAgent()

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value={}
    ):
        result = await agent.run(
            FramerInput(
                case_title="Test",
                problem_statement="Popis problému",
            )
        )

    assert result.scope == "Popis problému"  # fallback z problem_statement
    assert result.a3_structure == [
        "Pozadí",
        "Současný stav",
        "Kořenové příčiny",
        "Řešení",
        "Plán",
    ]
    assert result.key_questions == []