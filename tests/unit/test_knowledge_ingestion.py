"""Unit testy pro knowledge/ingestion.py — A3 ingestion pipeline."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from src.knowledge.ingestion import IngestionPipeline
from src.knowledge.retrieval import HybridRetriever


def test_ingest_anonymizes_before_store() -> None:
    pipeline = IngestionPipeline()
    doc = {
        "title": "Zprava klienta",
        "content": "Kontakt: jan.novak@firma.cz, problem s dashboardem.",
        "source": "client",
    }
    anonymized = pipeline.anonymizer.anonymize(doc)
    assert "[REDACTED_EMAIL]" in anonymized["content"]
    assert "jan.novak@firma.cz" not in anonymized["content"]
    assert anonymized["source"] == "client"


def test_ingest_batch_count() -> None:
    # Každý test musí pracovat s vlastní izolovanou databází, aby výsledek
    # nezávisel na dokumentech vložených předchozími testy do sdílené
    # data/retrieval.db.
    with tempfile.TemporaryDirectory() as tmp:
        retriever = HybridRetriever(db_path=str(Path(tmp) / "retrieval.db"))
        pipeline = IngestionPipeline(retriever=retriever)
        docs = [
            {"title": f"D{i}", "content": f"obsah {i}", "source": "s"} for i in range(3)
        ]

        async def _run() -> dict:
            return await pipeline.ingest_batch(docs)

        result = asyncio.run(_run())
        assert result["status"] == "batch_ingested"
        assert result["count"] == 3
        assert len(pipeline.retriever.get_all()) == 3
