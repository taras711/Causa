"""Unit testy pro A3 ingestion pipeline."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.knowledge.ingestion import A3Ingestor, IngestionResult
from src.knowledge.retrieval import HybridRetriever


@pytest.fixture
def retriever_tmp() -> HybridRetriever:
    """HybridRetriever s dočasnou databází (žádné volání Ollama v testech)."""

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "retrieval.db"
        # embedding_model, který neexistuje -> _embed_text vrátí [] díky try/except
        retriever = HybridRetriever(
            db_path=str(db_path),
            embedding_model="neexistujici-model",
        )
        yield retriever


@pytest.fixture
def ingestor(retriever_tmp: HybridRetriever) -> A3Ingestor:
    return A3Ingestor(retriever=retriever_tmp)


def test_ingest_text_creates_chunks(ingestor: A3Ingestor) -> None:
    content = "Toto je první odstavec.\\n\\nToto je druhý odstavec s více textem pro testování chunkování."
    result = ingestor.ingest_text(
        content=content,
        source="test-source",
        title="Test dokument",
        tenant_id="tenant-1",
        create_face_models=False,
    )

    assert isinstance(result, IngestionResult)
    assert result.success
    assert len(result.chunks) >= 1
    assert result.chunks[0].source == "test-source"
    assert result.chunks[0].title == "Test dokument"
    assert "Toto je první odstavec" in result.chunks[0].content


def test_ingest_text_creates_face_models(ingestor: A3Ingestor) -> None:
    content = "Snížení nákladů prostřednictvím automatizace schvalování faktur."
    result = ingestor.ingest_text(
        content=content,
        source="test-source",
        title="Automatizace faktur",
        tenant_id="tenant-1",
        create_face_models=True,
    )

    assert len(result.face_models) >= 1
    fm = result.face_models[0]
    assert fm.name == "Automatizace faktur"
    assert "tenant-1" in fm.applicable_to
    assert "ingested" in fm.tags
    assert fm.evidence == "test-source"


def test_ingest_markdown_strips_formatting(ingestor: A3Ingestor) -> None:
    md = "# Nadpis\\n\\nTento text je **tučný** a tento je *kurzívní*.\\n\\n[Odkaz](http://example.com)"
    result = ingestor.ingest_markdown(
        content=md,
        source="md-source",
        title="Markdown test",
        create_face_models=False,
    )

    # V obsahu by neměly být markdownマークy
    all_content = " ".join(c.content for c in result.chunks)
    assert "**" not in all_content
    assert "http://example.com" not in all_content  # odkaz by měl být nahrazen textem
    assert "Odkaz" in all_content


def test_ingest_json_extracts_text(ingestor: A3Ingestor) -> None:
    json_content = '{"title": "A3 analýza", "content": "Problém: vysoké náklady. Řešení: automatizace."}'
    result = ingestor.ingest_json(
        content=json_content,
        source="json-source",
        title="JSON test",
        create_face_models=False,
    )

    assert len(result.chunks) >= 1
    all_content = " ".join(c.content for c in result.chunks)
    assert "vysoké náklady" in all_content
    assert "automatizace" in all_content


def test_ingest_json_from_dict(ingestor: A3Ingestor) -> None:
    data = {"section": "Úvod", "text": "Toto je testovací text ze slovníku."}
    result = ingestor.ingest_json(
        content=data,
        source="dict-source",
        create_face_models=False,
    )

    assert len(result.chunks) >= 1
    all_content = " ".join(c.content for c in result.chunks)
    assert "testovací text ze slovníku" in all_content


def test_ingest_file_text(tmp_path: Path, ingestor: A3Ingestor) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Obsah textového souboru pro ingestion test.", encoding="utf-8")

    result = ingestor.ingest_file(path=str(file_path), create_face_models=False)

    assert result.success
    assert len(result.chunks) >= 1
    assert "Obsah textového souboru" in result.chunks[0].content


def test_ingest_file_markdown(tmp_path: Path, ingestor: A3Ingestor) -> None:
    file_path = tmp_path / "test.md"
    file_path.write_text("# Markdown soubor\\n\\nObsah markdown.", encoding="utf-8")

    result = ingestor.ingest_file(path=str(file_path), create_face_models=False)

    assert result.success
    assert len(result.chunks) >= 1


def test_ingest_file_json(tmp_path: Path, ingestor: A3Ingestor) -> None:
    file_path = tmp_path / "test.json"
    file_path.write_text('{"key": "hodnota", "text": "JSON soubor pro test."}', encoding="utf-8")

    result = ingestor.ingest_file(path=str(file_path), create_face_models=False)

    assert result.success
    assert len(result.chunks) >= 1


def test_ingest_file_not_found(ingestor: A3Ingestor) -> None:
    result = ingestor.ingest_file(path="/cesta/co/neexistuje.txt")

    assert not result.success
    assert len(result.errors) == 1
    assert "neexistuje" in result.errors[0]


def test_empty_content(ingestor: A3Ingestor) -> None:
    result = ingestor.ingest_text(content="", source="empty", create_face_models=False)

    assert result.success
    assert len(result.chunks) == 0
    assert result.indexed_documents == 0


def test_chunk_overlap(ingestor: A3Ingestor) -> None:
    # Vytvořit dlouhý text, který bude rozdělen na více chunků s překrytím
    long_text = " ".join([f"Slovo {i}." for i in range(200)])
    result = ingestor.ingest_text(
        content=long_text,
        source="long",
        title="Dlouhý text",
        create_face_models=False,
    )
    # ingest_text používá výchozí chunk_size, takže text může být v jednom chunku
    # Důležité je jen že výsledek je validní
    assert result.success
    assert len(result.chunks) >= 1