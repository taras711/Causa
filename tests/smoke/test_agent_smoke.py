"""Fumé testy proti živému Ollama modelu.

Vyžadují spuštěný Ollama server na ``http://localhost:11434`` a stažené modely.
Pokud Ollama není dostupný, testy se přeskočí (nikoliv selžou).
"""
from __future__ import annotations

import ollama

import pytest

from src.agents.framer import FramerAgent, FramerInput

OLLAMA_URL = "http://localhost:11434"


def _ollama_reachable() -> bool:
    try:
        ollama.Client(host=OLLAMA_URL).list()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_reachable(),
    reason="Ollama server není dostupný na http://localhost:11434",
)


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_framer_agent_live_ollama_returns_valid_output() -> None:
    """Skutečný agent Framer zavolá živý model qwen3.5:4b přes Ollama."""
    agent = FramerAgent(ollama_base_url=OLLAMA_URL)
    assert agent.model_name == "qwen3.5:4b"
    assert agent.autonomy.value == "L1"

    result = await agent.run(
        FramerInput(
            case_title="Kouřový test",
            problem_statement="Ověřit, že agenta lze volat proti živému Ollama modelu.",
            context={"industry": "e-commerce"},
        )
    )

    assert isinstance(result.scope, str) and result.scope
    assert isinstance(result.a3_structure, list) and len(result.a3_structure) >= 1
    assert all(isinstance(item, str) and item for item in result.a3_structure)
    assert isinstance(result.key_questions, list)
