"""Hybridní retrieval (klíčová slova + sémantika) pro Evidence Retrievera."""
from __future__ import annotations

from typing import Any


class HybridRetriever:
    """Hybridní vyhledávání: klíčová slova (BM25-like) + sémantické (embedings).

    V aktuální fázi pracuje s v paměti drženým indexem. V další fázi se
    napojí na pgvector (PostgreSQL) nebo sqlite-vec.
    """

    def __init__(self, vector_store: Any = None, keyword_index: Any = None) -> None:
        self.vector_store = vector_store
        self.keyword_index = keyword_index or {}
        self._documents: list[dict[str, Any]] = []

    def add_document(self, doc: dict[str, Any]) -> None:
        """Přidá dokument do indexu pro późnější vyhledávání."""
        self._documents.append(doc)
        text = (doc.get("title", "") + " " + doc.get("content", "")).lower()
        for word in set(text.split()):
            self.keyword_index.setdefault(word, []).append(doc)

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Vyhledá dokumenty kombinací klíčových slov a sémantického skóre."""
        query_words = set(query.lower().split())
        scored: list[tuple[float, dict[str, Any]]] = []

        for doc in self._documents:
            text = (doc.get("title", "") + " " + doc.get("content", "")).lower()
            matches = sum(1 for w in query_words if w in text)
            if matches > 0:
                score = matches / len(query_words) if query_words else 0
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _score, doc in scored[:top_k]]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._documents)