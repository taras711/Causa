"""HybridnĂ­ retrieval (klĂ­ÄŤovĂˇ slova + sĂ©mantika) pro Evidence Retrievera.

Kombinuje keyword-based vyhledĂˇvĂˇnĂ­ s sĂ©mantickĂ˝m vyhledĂˇvĂˇnĂ­m pĹ™es Ollama
embeddings (model nomic-embed-text). Dokumenty jsou trvale uloĹľeny v SQLite.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ollama import embeddings  # type: ignore[import-untyped]

from src.config.settings import Settings


class HybridRetriever:
    """HybridnĂ­ vyhledĂˇvĂˇnĂ­: klĂ­ÄŤovĂˇ slova (BM25-like) + sĂ©mantickĂ© (embedings).

    Dokumenty jsou indexovĂˇny v pamÄ›ti a trvale uloĹľeny v SQLite.
    SĂ©mantickĂ© skĂłre se poÄŤĂ­tĂˇ jako kosinovĂˇ podobnost mezi embeddingem
    dotazu a embeddingem dokumentu.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        vector_store: Any = None,
        keyword_index: Any = None,
        ollama_base_url: str = "http://localhost:11434",
        embedding_model: str | None = None,
    ) -> None:
        self.settings = Settings()
        self.ollama_base_url = ollama_base_url
        self.embedding_model = embedding_model or self.settings.model_embedding

        self.vector_store = vector_store
        self.keyword_index = keyword_index or {}
        self._documents: list[dict[str, Any]] = []
        self._embeddings: list[list[float]] = []

        # TrvalĂ© ĂşloĹľiĹˇtÄ›
        if db_path is None:
            db_path = Path("data") / "retrieval.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_from_db()

    # ------------------------------------------------------------------ #
    # DatabĂˇzovĂ© operace
    # ------------------------------------------------------------------ #

    def _init_db(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS retrieval_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL DEFAULT '',
                    source TEXT,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_retrieval_docs_source "
                "ON retrieval_documents(source)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS retrieval_embeddings (
                    doc_id TEXT PRIMARY KEY,
                    embedding TEXT NOT NULL,
                    FOREIGN KEY(doc_id) REFERENCES retrieval_documents(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _load_from_db(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        try:
            rows = conn.execute(
                "SELECT id, title, content, source, metadata FROM retrieval_documents"
            ).fetchall()
            for row in rows:
                doc = {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "source": row[3],
                    "metadata": self._safe_json(row[4]),
                }
                self._documents.append(doc)
                text = (str(doc.get("title") or "") + " " + str(doc.get("content") or "")).lower()
                for word in set(text.split()):
                    self.keyword_index.setdefault(word, []).append(doc)

                emb_row = conn.execute(
                    "SELECT embedding FROM retrieval_embeddings WHERE doc_id = ?",
                    (row[0],),
                ).fetchone()
                if emb_row:
                    try:
                        self._embeddings.append(json.loads(emb_row[0]))
                    except (json.JSONDecodeError, TypeError, ValueError):
                        self._embeddings.append([])
                else:
                    self._embeddings.append([])
        finally:
            conn.close()

    def _persist_document(self, doc: dict[str, Any], embedding: list[float]) -> None:
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO retrieval_documents
                (id, title, content, source, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    doc.get("id", ""),
                    doc.get("title", ""),
                    doc.get("content", ""),
                    doc.get("source"),
                    json.dumps(doc.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO retrieval_embeddings (doc_id, embedding)
                VALUES (?, ?)
                """,
                (doc.get("id", ""), json.dumps(embedding)),
            )
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    # Embeddings
    # ------------------------------------------------------------------ #

    def _embed_text(self, text: str) -> list[float]:
        """VypoÄŤĂ­tĂˇ embedding pro danĂ˝ text pĹ™es Ollama embeddings API."""

        try:
            response = embeddings(
                model=self.embedding_model,
                prompt=text,
                base_url=self.ollama_base_url,
            )
            return response.get("embedding", [])
        except Exception:
            # V pĹ™Ă­padÄ› chyby vrĂˇtĂ­me prĂˇzdnĂ˝ vektor (sĂ©mantickĂ© skĂłre bude 0)
            return []

    @staticmethod
    def _safe_json(value: Any) -> Any:
        if not value:
            return {}
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    # ------------------------------------------------------------------ #
    # VeĹ™ejnĂ© rozhranĂ­
    # ------------------------------------------------------------------ #

    def add_document(self, doc: dict[str, Any]) -> None:
        """PĹ™idĂˇ dokument do indexu (keyword + sĂ©mantickĂ˝ embedding)."""
        if not isinstance(doc, dict):
            doc = {}

        title = doc.get("title", "")
        content = doc.get("content", "")
        title = "" if title is None else str(title)
        content = "" if content is None else str(content)
        doc = dict(doc)
        doc["title"] = title
        doc["content"] = content

        self._documents.append(doc)
        text = (title + " " + content).lower()
        for word in set(text.split()):
            self.keyword_index.setdefault(word, []).append(doc)

        # VypoÄŤĂ­tat a uloĹľit embedding
        embedding_text = title + " " + content
        embedding = self._embed_text(embedding_text)
        self._embeddings.append(embedding)

        try:
            self._persist_document(doc, embedding)
        except Exception:
            # DatabĂˇzovĂˇ chyba by nemÄ›la blokovat bÄ›h v pamÄ›ti
            pass

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """VyhledĂˇ dokumenty kombinacĂ­ klĂ­ÄŤovĂ˝ch slov a sĂ©mantickĂ©ho skĂłre.

        VĂˇha: 40 % klĂ­ÄŤovĂˇ slova, 60 % sĂ©mantickĂˇ podobnost.
        """
        return await self.hybrid_search(query, top_k=top_k)

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        keyword_weight: float = 0.4,
        semantic_weight: float = 0.6,
    ) -> list[dict[str, Any]]:
        """KombinovanĂ© vyhledĂˇvĂˇnĂ­ s nastavitelnĂ˝mi vĂˇhami."""
        query = "" if query is None else str(query)
        try:
            top_k = int(top_k)
        except (TypeError, ValueError):
            top_k = 5

        query_words = set(query.lower().split())
        query_embedding = self._embed_text(query)

        scored: list[tuple[float, dict[str, Any]]] = []

        for idx, doc in enumerate(self._documents):
            # Keyword skĂłre
            text = (str(doc.get("title") or "") + " " + str(doc.get("content") or "")).lower()
            matches = sum(1 for w in query_words if w in text)
            keyword_score = matches / len(query_words) if query_words else 0.0

            # SĂ©mantickĂ© skĂłre
            doc_embedding = self._embeddings[idx] if idx < len(self._embeddings) else []
            semantic_score = self._cosine_similarity(query_embedding, doc_embedding)

            combined = keyword_weight * keyword_score + semantic_weight * semantic_score
            if combined > 0:
                scored.append((combined, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _score, doc in scored[:top_k]]

    async def keyword_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Pouze keyword-based vyhledĂˇvĂˇnĂ­ (zpÄ›tnĂˇ kompatibilita)."""

        query_words = set(query.lower().split())
        scored: list[tuple[float, dict[str, Any]]] = []

        for doc in self._documents:
            text = (str(doc.get("title") or "") + " " + str(doc.get("content") or "")).lower()
            matches = sum(1 for w in query_words if w in text)
            if matches > 0:
                score = matches / len(query_words) if query_words else 0
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _score, doc in scored[:top_k]]

    async def semantic_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Pouze sĂ©mantickĂ© vyhledĂˇvĂˇnĂ­ pĹ™es Ollama embeddings."""

        query_embedding = self._embed_text(query)
        scored: list[tuple[float, dict[str, Any]]] = []

        for idx, doc in enumerate(self._documents):
            doc_embedding = self._embeddings[idx] if idx < len(self._embeddings) else []
            score = self._cosine_similarity(query_embedding, doc_embedding)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _score, doc in scored[:top_k]]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._documents)

