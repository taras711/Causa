"""A3 ingestion pipeline s povinnou anonymizací před uložením."""
from __future__ import annotations

from src.knowledge.anonymization import Anonymizer


class IngestionPipeline:
    def __init__(self, anonymizer: Anonymizer | None = None) -> None:
        self.anonymizer = anonymizer or Anonymizer()

    async def ingest(self, document: dict) -> dict:
        anonymized = self.anonymizer.anonymize(document)
        # Uloží se do znalostní báze (v další fázi pgvector / sqlite-vec)
        return {"status": "ingested", "anonymized": True, "doc": anonymized}