"""Unit testy pro EvidenceRetrieverAgenta (s mocknutým retrieverem)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.agents.evidence_retriever import (
    EvidenceRetrieverAgent,
    EvidenceRetrieverInput,
)


@pytest.mark.asyncio
async def test_retriever_without_retriever_returns_empty() -> None:
    agent = EvidenceRetrieverAgent(retriever=None)

    result = await agent.run(
        EvidenceRetrieverInput(query="náklady", top_k=5)
    )

    assert result.results == []
    assert result.sources == []


@pytest.mark.asyncio
async def test_retriever_uses_injected_retriever() -> None:
    mock_retriever = AsyncMock()
    mock_retriever.search.return_value = [
        {"source": "dokument.pdf", "text": "náklady klesly", "score": 0.95},
        {"source": "email.txt", "text": "rozpočet 2024", "score": 0.8},
    ]

    agent = EvidenceRetrieverAgent(retriever=mock_retriever)

    result = await agent.run(
        EvidenceRetrieverInput(query="náklady", top_k=2)
    )

    assert len(result.results) == 2
    assert result.sources == ["dokument.pdf", "email.txt"]
    mock_retriever.search.assert_awaited_once_with(query="náklady", top_k=2)