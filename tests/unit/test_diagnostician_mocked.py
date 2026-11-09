"""Unit testy pro DiagnosticianAgenta s mocknutým Ollama voláním."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.diagnostician import DiagnosticianAgent, DiagnosticianInput


@pytest.mark.asyncio
async def test_diagnostician_run_returns_root_causes() -> None:
    agent = DiagnosticianAgent()

    mocked_response = {
        "root_causes": ["Neefektivní proces", "Nedostatek dat"],
        "contributing_factors": ["Lidská chyba"],
        "confidence": 0.9,
    }

    with patch.object(
        agent, "_call_ollama_json", new_callable=AsyncMock, return_value=mocked_response
    ):
        result = await agent.run(
            DiagnosticianInput(
                scope="Optimalizace nákladů",
                evidence=["Výkaz zisků 2024"],
            )
        )

    assert result.root_causes == ["Neefektivní proces", "Nedostatek dat"]
    assert result.contributing_factors == ["Lidská chyba"]
    assert result.confidence == 0.9


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
    assert result.confidence == 0.5