"""Unit testy pro VerifierAgenta s mocknutým Ollama voláním."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.verifier import VerifierAgent, VerifierInput


@pytest.mark.asyncio
async def test_verifier_returns_verification_result() -> None:
    agent = VerifierAgent()

    mocked_response = {
        "verified": True,
        "verification_level": "verified",
        "notes": "Tvrzení je podloženo finančním výkazem.",
    }

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value=mocked_response
    ):
        result = await agent.run(
            VerifierInput(
                claim_text="Výnos klesl o 10 %",
                source="client_data",
                evidence="Finanční výkaz 2024",
            )
        )

    assert result.verified is True
    assert result.verification_level == "verified"
    assert "finančním výkazem" in result.notes


@pytest.mark.asyncio
async def test_verifier_invalid_level_defaults_to_unverified() -> None:
    agent = VerifierAgent()

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value={
            "verified": False,
            "verification_level": "unknown_level",
            "notes": "",
        }
    ):
        result = await agent.run(
            VerifierInput(claim_text="Test", source="assumption")
        )

    assert result.verification_level == "unverified"
    assert result.verified is False