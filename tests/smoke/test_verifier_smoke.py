"""Fumé test pro Verifier agenta proti živému Ollama modelu (qwen3:14b).

Vyžaduje spuštěný Ollama na http://localhost:11434 a stažený model qwen3:14b.
Při nedostupnosti Ollama se test přeskočí.
"""
from __future__ import annotations

import ollama
import pytest

from src.agents.verifier import VerifierAgent, VerifierInput

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
async def test_verifier_agent_live_ollama_returns_valid_output() -> None:
    """Skutečný agent Verifier zavolá živý model qwen3:14b přes Ollama."""
    agent = VerifierAgent(ollama_base_url=OLLAMA_URL)
    assert agent.model_name == "qwen3:14b"
    assert agent.autonomy.value == "L2"

    result = await agent.run(
        VerifierInput(
            claim_text="Výnos klesl o 10 %",
            source="client_data",
            evidence="Finanční výkaz 2024",
        )
    )

    assert result.verification_level in ("unverified", "partial", "verified")
    assert isinstance(result.verified, bool)
    assert isinstance(result.notes, str)
