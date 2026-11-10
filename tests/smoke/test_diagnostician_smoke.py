"""Fumé test pro Diagnostician agenta proti živému Ollama modelu (qwen3:14b).

Vyžaduje spuštěný Ollama na http://localhost:11434 a stažený model qwen3:14b.
Při nedostupnosti Ollama se test přeskočí.
"""
from __future__ import annotations

import ollama
import pytest

from src.agents.diagnostician import DiagnosticianAgent, DiagnosticianInput

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
async def test_diagnostician_agent_live_ollama_returns_valid_output() -> None:
    """Skutečný agent Diagnostician zavolá živý model qwen3:14b přes Ollama."""
    agent = DiagnosticianAgent(ollama_base_url=OLLAMA_URL)
    assert agent.model_name == "qwen3:14b"
    assert agent.autonomy.value == "L1"

    result = await agent.run(
        DiagnosticianInput(
            scope="Nákladové úspory",
            evidence=[
                "Vysoké režijní náklady v provozu",
                "Nedostatečná automatizace schvalování",
            ],
            context={"industry": "e-commerce"},
        )
    )

    assert isinstance(result.root_causes, list) and len(result.root_causes) >= 1
    assert all(isinstance(item, str) and item for item in result.root_causes)
    assert isinstance(result.contributing_factors, list)
    assert 0.0 <= result.confidence <= 1.0
