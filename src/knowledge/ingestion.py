"""A3 ingestion pipeline s povinnou anonymizací před uložením."""
from __future__ import annotations

from typing import Any

from src.knowledge.anonymization import Anonymizer
from src.knowledge.retrieval import HybridRetriever


class IngestionPipeline:
    """Pipeline pro ingestion dokumentů do znalostní báze.

    Každý dokument projde anonymizací před uložením. Výsledkem je
    anonymizovaný dokument připravený k indexování.
    """

    def __init__(
        self,
        anonymizer: Anonymizer | None = None,
        retriever: HybridRetriever | None = None,
    ) -> None:
        self.anonymizer = anonymizer or Anonymizer()
        self.retriever = retriever or HybridRetriever()

    async def ingest(self, document: dict[str, Any]) -> dict[str, Any]:
        anonymized = self.anonymizer.anonymize(document)
        self.retriever.add_document(anonymized)
        return {
            "status": "ingested",
            "anonymized": True,
            "doc": anonymized,
        }

    async def ingest_batch(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        """Ingestuje více dokumentů najednou."""
        results = []
        for doc in documents:
            result = await self.ingest(doc)
            results.append(result)
        return {
            "status": "batch_ingested",
            "count": len(results),
            "results": results,
        }