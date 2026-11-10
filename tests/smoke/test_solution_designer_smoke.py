"""Fumé test pro SolutionDesigner agenta proti živému Ollama modelu (qwen3:14b).

Vyžaduje spuštěný Ollama na http://localhost:11434 a stažený model qwen3:14b.
Při nedostupnosti Ollama se test přeskočí.
"""
from __future__ import annotations

import ollama
import pytest

from src.agents.solution_designer import SolutionDesignerAgent, SolutionDesignerInput

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
async def test_solution_designer_agent_live_ollama_returns_valid_output() -> None:
    """Skutečný agent SolutionDesigner zavolá živý model qwen3:14b přes Ollama."""
    agent = SolutionDesignerAgent(ollama_base_url=OLLAMA_URL)
    assert agent.model_name == "qwen3:14b"
    assert agent.autonomy.value == "L1"

    result = await agent.run(
        SolutionDesignerInput(
            root_causes=["Neefektivní schvalovací proces", "Nedostatečná automatizace"],
            evidence=["Výkaz zisků a ztrát 2024"],
            context={"industry": "e-commerce"},
        )
    )

    assert isinstance(result.solutions, list) and len(result.solutions) >= 1
    assert all(isinstance(item, dict) for item in result.solutions)
    assert result.estimated_roi is None or (0.0 <= result.estimated_roi <= 100.0)
    assert 0.0 <= result.confidence <= 1.0
