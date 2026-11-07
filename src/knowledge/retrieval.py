"""Hybridní retrieval (klíčová slova + sémantika) pro Evidence Retrievera."""
from __future__ import annotations

from typing import Any


class HybridRetriever:
    def __init__(self, vector_store: Any = None, keyword_index: Any = None) -> None:
        self.vector_store = vector_store
        self.keyword_index = keyword_index

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        # Placeholder – napojí se na pgvector / sqlite-vec v další fázi
        return []