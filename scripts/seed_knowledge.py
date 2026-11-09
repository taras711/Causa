"""Seed skript pro naplnění knowledge base kurátorskými záznamy.

Seed data jsou verzeována v `configs/seed/seed_records.json` (pro nasazení
u zákazníka/design partnera) s fallbackem na lokální `data/knowledge/`
při vývoji.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from src.knowledge.ingestion import IngestionPipeline

# Verzeovaná kopie seed dat (přednostní) s fallbackem na data/ adresář.
CONFIG_SEED_PATH = (
    Path(__file__).resolve().parent.parent / "configs" / "seed" / "seed_records.json"
)
DATA_SEED_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "knowledge" / "seed_records.json"
)


def _resolve_seed_path() -> Path:
    """Vrátí existující cestu k seed datům (verzeovaná přednostně)."""
    if CONFIG_SEED_PATH.exists():
        return CONFIG_SEED_PATH
    return DATA_SEED_PATH


SEED_PATH = _resolve_seed_path()


def load_seed_records() -> list[dict]:
    with open(SEED_PATH, encoding="utf-8-sig") as f:
        return json.load(f)


async def seed_knowledge_base() -> None:
    """Naplní knowledge base ze seed_records.json přes ingestion pipeline."""
    records = load_seed_records()
    print(f"Nalezeno {len(records)} seed záznamů k ingestaci.")

    pipeline = IngestionPipeline()
    result = await pipeline.ingest_batch(records)

    print(f"Status: {result['status']}")
    print(f"Počet ingestovaných záznamů: {result['count']}")
    print(f"Celkem v indexu: {len(pipeline.retriever.get_all())}")


def seed_sync() -> None:
    asyncio.run(seed_knowledge_base())


if __name__ == "__main__":
    seed_sync()
