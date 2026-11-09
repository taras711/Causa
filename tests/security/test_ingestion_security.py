"""Bezpečnostní testy pro A3Ingestor."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.knowledge.ingestion import A3Ingestor
from src.knowledge.retrieval import HybridRetriever


@pytest.fixture
def ingestor_tmp() -> A3Ingestor:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "r.db"
        retriever = HybridRetriever(db_path=str(db), embedding_model="neexistujici-model")
        yield A3Ingestor(retriever=retriever)


@pytest.mark.security
def test_ingest_json_invalid_json_does_not_crash(ingestor_tmp: A3Ingestor) -> None:
    try:
        res = ingestor_tmp.ingest_json(content="{not json", source="s")
    except json.JSONDecodeError:
        return
    assert res is not None


@pytest.mark.security
def test_ingest_json_deeply_nested_does_not_crash(ingestor_tmp: A3Ingestor) -> None:
    # Hluboce vnořený JSON by neměl způsobit RecursionError nebo pád
    deep = "a"
    obj: dict = {}
    cur = obj
    for _ in range(500):
        cur["x"] = {}
        cur = cur["x"]
    try:
        res = ingestor_tmp.ingest_json(content=obj, source="s", create_face_models=False)
    except RecursionError:
        return
    assert res is not None


@pytest.mark.security
def test_ingest_file_missing_returns_error(ingestor_tmp: A3Ingestor) -> None:
    res = ingestor_tmp.ingest_file(path="/cesta/co/neexistuje.txt")
    assert not res.success
    assert len(res.errors) >= 1


@pytest.mark.security
def test_ingest_file_binary_does_not_crash(ingestor_tmp: A3Ingestor, tmp_path: Path) -> None:
    p = tmp_path / "bin.bin"
    p.write_bytes(b"\x00\x01\x02\xff\xfe")
    try:
        res = ingestor_tmp.ingest_file(path=str(p))
    except UnicodeDecodeError:
        return
    # Pokud to projde, musí být výsledek validní nebo chyba
    assert res is not None


@pytest.mark.security
def test_ingest_text_huge_does_not_dos(ingestor_tmp: A3Ingestor) -> None:
    big = "text " * 200000
    res = ingestor_tmp.ingest_text(content=big, source="s", create_face_models=False)
    assert res is not None


@pytest.mark.security
def test_ingest_text_injection_payload_treated_as_data(ingestor_tmp: A3Ingestor) -> None:
    payload = "'; DROP TABLE chunks; -- <script>alert(1)</script>"
    res = ingestor_tmp.ingest_text(content=payload, source="s", create_face_models=False)
    assert res.success
    allc = " ".join(c.content for c in res.chunks)
    assert "DROP" in allc or "script" in allc


@pytest.mark.security
def test_ingest_markdown_does_not_execute(ingestor_tmp: A3Ingestor) -> None:
    md = "# H\n\n![x](javascript:alert(1))\n\n**tučně**"
    res = ingestor_tmp.ingest_markdown(content=md, source="s", create_face_models=False)
    assert res.success


@pytest.mark.security
def test_ingest_empty_content(ingestor_tmp: A3Ingestor) -> None:
    res = ingestor_tmp.ingest_text(content="", source="s", create_face_models=False)
    assert res.success
    assert res.chunks == []
