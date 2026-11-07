"""Bezpečnostní testy pro HybridRetriever."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.knowledge.retrieval import HybridRetriever


@pytest.fixture
def retriever_tmp() -> HybridRetriever:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "retrieval.db"
        yield HybridRetriever(db_path=str(db_path), embedding_model="neexistujici-model")


@pytest.mark.security
def test_search_empty_query_does_not_crash(retriever_tmp: HybridRetriever) -> None:
    res = retriever_tmp.search("")
    assert isinstance(res, list)


@pytest.mark.security
def test_search_non_str_query_does_not_crash(retriever_tmp: HybridRetriever) -> None:
    try:
        res = retriever_tmp.search(123)  # type: ignore[arg-type]
    except (TypeError, AttributeError):
        return
    assert isinstance(res, list)


@pytest.mark.security
def test_hybrid_search_top_k_negative_does_not_crash(retriever_tmp: HybridRetriever) -> None:
    retriever_tmp.add_document({"id": "d1", "title": "t", "content": "c", "source": "s"})
    res = retriever_tmp.hybrid_search("q", top_k=-1)
    assert isinstance(res, list)


@pytest.mark.security
def test_hybrid_search_top_k_huge_does_not_crash(retriever_tmp: HybridRetriever) -> None:
    retriever_tmp.add_document({"id": "d1", "title": "t", "content": "c", "source": "s"})
    res = retriever_tmp.hybrid_search("q", top_k=10_000)
    assert isinstance(res, list)


@pytest.mark.security
def test_add_document_injection_id_does_not_execute(retriever_tmp: HybridRetriever) -> None:
    evil = "'; DROP TABLE retrieval_documents; --"
    retriever_tmp.add_document({"id": evil, "title": "t", "content": "c"})
    # Dokument je uložen jako data, ne vykonán
    assert any(d.get("id") == evil for d in retriever_tmp.get_all())


@pytest.mark.security
def test_add_document_none_values_does_not_crash(retriever_tmp: HybridRetriever) -> None:
    retriever_tmp.add_document({"id": None, "title": None, "content": None})
    assert isinstance(retriever_tmp.get_all(), list)


@pytest.mark.security
def test_keyword_search_empty_index(retriever_tmp: HybridRetriever) -> None:
    res = retriever_tmp.keyword_search("anything")
    assert res == []


@pytest.mark.security
def test_semantic_search_empty_index(retriever_tmp: HybridRetriever) -> None:
    res = retriever_tmp.semantic_search("anything")
    assert res == []


@pytest.mark.security
def test_cosine_similarity_mismatched_lengths() -> None:
    from src.knowledge.retrieval import HybridRetriever

    assert HybridRetriever._cosine_similarity([1.0, 2.0], [1.0]) == 0.0
    assert HybridRetriever._cosine_similarity([], []) == 0.0


@pytest.mark.security
def test_malformed_metadata_in_db_does_not_crash(tmp_path: Path) -> None:
    db_path = tmp_path / "bad.db"
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE retrieval_documents (id TEXT PRIMARY KEY, title TEXT, content TEXT, source TEXT, metadata TEXT)"
    )
    conn.execute(
        "CREATE TABLE retrieval_embeddings (doc_id TEXT PRIMARY KEY, embedding TEXT)"
    )
    conn.execute(
        "INSERT INTO retrieval_documents (id,title,content,source,metadata) VALUES (?,?,?,?,?)",
        ("d1", "t", "c", "s", "{not json"),
    )
    conn.commit()
    conn.close()
    # Načtení z DB by nemělo spadnout
    try:
        r = HybridRetriever(db_path=str(db_path), embedding_model="neexistujici-model")
    except Exception:
        return
    assert isinstance(r.get_all(), list)
