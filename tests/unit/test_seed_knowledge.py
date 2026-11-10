"""Unit testy pro seed data knowledge base (příprava pilotu s design partnerem).

Ověřují, že verzeovaná seed data jsou platná, obsahují povinná pole a že
ingestní pipeline přijme všechny záznamy (připravenost pro pilot).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.knowledge.ingestion import IngestionPipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_PATH = PROJECT_ROOT / "configs" / "seed" / "seed_records.json"

REQUIRED_FIELDS = {"title", "content", "source", "category", "confidence"}


def _load_records() -> list[dict]:
    with open(SEED_PATH, encoding="utf-8-sig") as f:
        return json.load(f)


def test_seed_file_exists_and_is_valid_json() -> None:
    """Seed soubor musí existovat a být platný JSON."""
    assert SEED_PATH.exists(), f"Chybí verzeovaný seed soubor: {SEED_PATH}"
    records = _load_records()
    assert isinstance(records, list)
    assert len(records) >= 30  # roadmapa: 30–50 kurátorovaných záznamů


def test_seed_records_have_required_fields() -> None:
    """Každý seed záznam musí mít povinná pole pro knowledge base."""
    records = _load_records()
    assert len(records) > 0
    for record in records:
        missing = REQUIRED_FIELDS - record.keys()
        assert not missing, f"Chybí pole {missing} v záznamu {record.get('id')}"
        assert 0.0 <= record["confidence"] <= 1.0, record.get("id")


def test_seed_records_do_not_leak_pii() -> None:
    """Seed data pro pilot nesmí obsahovat citlivé identifikátory klientů."""
    records = _load_records()
    text = json.dumps(records, ensure_ascii=False).lower()
    assert "@" not in text, "Seed data obsahují e-mailovou adresu"
    assert "+420" not in text, "Seed data obsahují telefonní číslo"
    assert "rodné číslo" not in text, "Seed data obsahují rodné číslo"


@pytest.mark.asyncio
async def test_seed_ingestion_accepts_all_records() -> None:
    """Ingestní pipeline přijme všechny seed záznamy (pilot readiness)."""
    records = _load_records()
    # Vytvoříme vlastní retriever s dočasnou databází pro izolaci testu
    import tempfile
    from pathlib import Path

    from src.knowledge.retrieval import HybridRetriever

    tmp = tempfile.mkdtemp()
    retriever = HybridRetriever(
        db_path=str(Path(tmp) / "retrieval.db"),
        embedding_model="neexistujici-model",
    )
    pipeline = IngestionPipeline(retriever=retriever)
    result = await pipeline.ingest_batch(records)
    assert result["status"] == "batch_ingested"
    assert result["count"] == len(records)
    assert len(pipeline.retriever.get_all()) == len(records)
