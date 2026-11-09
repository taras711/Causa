"""Unit testy pro hybridní retrieval (klíčová slova + sémantika)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.knowledge.retrieval import HybridRetriever


@pytest.fixture
def retriever_tmp() -> HybridRetriever:
    """HybridRetriever s dočasnou SQLite databází."""

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "retrieval.db"
        retriever = HybridRetriever(
            db_path=str(db_path),
            embedding_model="nomic-embed-text",
        )
        yield retriever


MOCK_EMBEDDING = [0.1, 0.2, 0.3, 0.4, 0.5]


@pytest.fixture
def mock_embeddings():
    """Mock Ollama embeddings - vrací konstantní vektor."""

    with patch(
        "src.knowledge.retrieval.embeddings",
        return_value={"embedding": MOCK_EMBEDDING},
    ) as m:
        yield m


def test_add_document_and_keyword_search(
    retriever_tmp: HybridRetriever, mock_embeddings
) -> None:
    """Přidání dokumentu a vyhledání podle klíčových slov."""

    retriever_tmp.add_document(
        {
            "id": "doc-1",
            "title": "Snížení nákladů",
            "content": "Automatizace schvalování faktur sníží režijní náklady o 20 %.",
            "source": "test",
        }
    )

    results = retriever_tmp.keyword_search("náklady automatizace", top_k=5)
    assert len(results) == 1
    assert results[0]["id"] == "doc-1"


def test_hybrid_search_returns_relevant_documents(
    retriever_tmp: HybridRetriever, mock_embeddings
) -> None:
    """Hybridní vyhledání vrátí relevantní dokumenty."""

    retriever_tmp.add_document(
        {
            "id": "doc-1",
            "title": "Lean Manufacturing",
            "content": "Eliminace plýtvání a kontinuální zlepšování procesů.",
            "source": "face_model",
        }
    )
    retriever_tmp.add_document(
        {
            "id": "doc-2",
            "title": "Finanční výkaz",
            "content": "Výnosy klesly o 10 %, náklady vzrostly o 5 %.",
            "source": "client_data",
        }
    )

    results = retriever_tmp.hybrid_search("plýtvání procesy", top_k=5)
    assert len(results) >= 1
    # První výsledek by měl být ten s "plýtvání" a "procesy"
    assert results[0]["id"] == "doc-1"


def test_semantic_search(mock_embeddings) -> None:
    """Pouze sémantické vyhledávání."""

    with tempfile.TemporaryDirectory() as tmp:
        retriever = HybridRetriever(
            db_path=str(Path(tmp) / "retrieval.db"),
            embedding_model="nomic-embed-text",
        )
        retriever.add_document(
            {
                "id": "doc-1",
                "title": "Test dokument",
                "content": "Obsah o optimalizaci procesů.",
                "source": "test",
            }
        )

    results = retriever.semantic_search("optimalizace", top_k=5)
    assert len(results) == 1
    assert results[0]["id"] == "doc-1"


def test_search_uses_hybrid_by_default(
    retriever_tmp: HybridRetriever, mock_embeddings
) -> None:
    """Metoda search deleguje na hybrid_search."""

    retriever_tmp.add_document(
        {
            "id": "doc-1",
            "title": "Test",
            "content": "Nějaký obsah pro vyhledávání.",
            "source": "test",
        }
    )

    results = retriever_tmp.search("obsah vyhledávání", top_k=5)
    assert len(results) == 1
    assert results[0]["id"] == "doc-1"


def test_empty_search_returns_empty_list(
    retriever_tmp: HybridRetriever, mock_embeddings
) -> None:
    """Vyhledávání v prázdném indexu vrací prázdný seznam."""

    results = retriever_tmp.search("cokoliv", top_k=5)
    assert results == []


def test_persistence_survives_reinit(mock_embeddings) -> None:
    """Dokumenty přidané do retrieveru přežijí jeho znovuinicializaci."""

    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "retrieval.db")

        # První instance - přidat dokument
        retriever1 = HybridRetriever(
            db_path=db_path, embedding_model="nomic-embed-text"
        )
        retriever1.add_document(
            {
                "id": "persistent-doc",
                "title": "Trvalý dokument",
                "content": "Tento dokument by měl zůstat uložen.",
                "source": "test",
            }
        )

        # Druhá instance - načíst ze stejné databáze
        retriever2 = HybridRetriever(
            db_path=db_path, embedding_model="nomic-embed-text"
        )

        # Třetí instance - opětovné načtení ze stejné databáze
        retriever3 = HybridRetriever(
            db_path=db_path, embedding_model="nomic-embed-text"
        )

    results = retriever3.keyword_search("trvalý dokument", top_k=5)
    assert len(results) == 1
    assert results[0]["id"] == "persistent-doc"


def test_get_all_returns_all_documents(
    retriever_tmp: HybridRetriever, mock_embeddings
) -> None:
    """get_all vrací všechny vložené dokumenty."""

    retriever_tmp.add_document(
        {"id": "d1", "title": "Jeden", "content": "Obsah 1", "source": "s1"}
    )
    retriever_tmp.add_document(
        {"id": "d2", "title": "Dva", "content": "Obsah 2", "source": "s2"}
    )

    all_docs = retriever_tmp.get_all()
    assert len(all_docs) == 2
    ids = {d["id"] for d in all_docs}
    assert ids == {"d1", "d2"}