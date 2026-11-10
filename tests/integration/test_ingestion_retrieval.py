"""Integrační testy: IngestionPipeline → anonymizace → uložení → retrieval."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from src.knowledge.anonymization import Anonymizer
from src.knowledge.ingestion import IngestionPipeline
from src.knowledge.retrieval import HybridRetriever


def _make_retriever() -> HybridRetriever:
    """Vytvoří retriever s vlastní dočasnou databází (izolace testů)."""
    tmp = tempfile.mkdtemp()
    return HybridRetriever(
        db_path=str(Path(tmp) / "retrieval.db"),
        embedding_model="nomic-embed-text",
    )


class TestIngestionRetrievalRoundtrip:
    """Dokument projde anonymizací, uloží se a je následně vyhledatelný."""

    @pytest.mark.asyncio
    async def test_ingested_document_is_searchable(self) -> None:
        retriever = _make_retriever()
        pipeline = IngestionPipeline(retriever=retriever)

        document = {
            "title": "5 Whys metoda",
            "content": "Metoda 5 Procku pomáhá najít kořenovou příčinu problému.",
            "category": "root_cause_analysis",
        }

        result = await pipeline.ingest(document)
        assert result["status"] == "ingested"
        assert len(retriever.get_all()) == 1

        found = await retriever.search("najít kořenovou příčinu", top_k=5)
        assert len(found) == 1
        assert found[0]["title"] == "5 Whys metoda"

    @pytest.mark.asyncio
    async def test_top_k_limits_results(self) -> None:
        retriever = _make_retriever()
        pipeline = IngestionPipeline(retriever=retriever)

        for i in range(5):
            await pipeline.ingest(
                {
                    "title": f"Dokument {i}",
                    "content": "klíčové slovo pro vyhledání",
                    "category": "test",
                }
            )

        found = await retriever.search("klíčové slovo", top_k=2)
        assert len(found) <= 2

    @pytest.mark.asyncio
    async def test_empty_query_returns_empty(self) -> None:
        retriever = _make_retriever()
        pipeline = IngestionPipeline(retriever=retriever)

        await pipeline.ingest({"title": "Jeden", "content": "nějaký obsah", "category": "x"})

        found = await retriever.search("", top_k=5)
        assert found == []

    @pytest.mark.asyncio
    async def test_search_with_no_matches_returns_empty(self) -> None:
        retriever = _make_retriever()
        pipeline = IngestionPipeline(retriever=retriever)

        await pipeline.ingest({"title": "Jeden", "content": "unikatni obsah", "category": "x"})

        found = await retriever.search("zcela neexistující dotaz", top_k=5)
        assert found == []

    @pytest.mark.asyncio
    async def test_anonymizer_is_applied_before_indexing(self) -> None:
        retriever = _make_retriever()
        pipeline = IngestionPipeline(retriever=retriever)

        document = {
            "title": "Zpráva",
            "content": "Kontakt: secret@firma.cz, IČO: ABC123456.",
        }

        await pipeline.ingest(document)

        # Obsah v indexu musí být anonymizován
        indexed = retriever.get_all()[0]
        indexed_str = str(indexed)
        assert "secret@firma.cz" not in indexed_str
        assert "ABC123456" not in indexed_str
        assert "[REDACTED_EMAIL]" in indexed_str
        assert "[REDACTED_ID]" in indexed_str
