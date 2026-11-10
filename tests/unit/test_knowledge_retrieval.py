"""Unit testy pro knowledge/retrieval.py — hybridni retrieval."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from src.knowledge.retrieval import HybridRetriever


def _make_retriever() -> HybridRetriever:
    """Vytvoří retriever s vlastní dočasnou databází (izolace testů)."""
    tmp = tempfile.mkdtemp()
    return HybridRetriever(
        db_path=str(Path(tmp) / "retrieval.db"),
        embedding_model="nomic-embed-text",
    )


def test_add_and_search_document() -> None:
    retriever = _make_retriever()
    retriever.add_document(
        {
            "title": "Root cause analysis",
            "content": "Korenova metoda pomaha najit korenove prinicily problemu.",
            "source": "lean_handbook",
        }
    )
    results = asyncio.run(retriever.search(query="korenove prinicily", top_k=5))
    assert len(results) == 1
    assert results[0]["title"] == "Root cause analysis"


def test_search_returns_empty_when_no_match() -> None:
    retriever = _make_retriever()
    retriever.add_document(
        {"title": "A", "content": "Financni analyza a ROI vypocty", "source": "quant"}
    )
    results = asyncio.run(retriever.search(query="neexistujici pojem xyz", top_k=5))
    assert results == []


def test_search_top_k_limit() -> None:
    retriever = _make_retriever()
    for i in range(5):
        retriever.add_document(
            {"title": f"Doc {i}", "content": "klicove slovo retrieval test", "source": "s"}
        )
    results = asyncio.run(retriever.search(query="klicove slovo", top_k=3))
    assert len(results) == 3


def test_get_all() -> None:
    retriever = _make_retriever()
    retriever.add_document({"title": "D1", "content": "obsah jedna", "source": "s"})
    retriever.add_document({"title": "D2", "content": "obsah dva", "source": "s"})
    all_docs = retriever.get_all()
    assert len(all_docs) == 2
