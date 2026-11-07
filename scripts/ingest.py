#!/usr/bin/env python3
"""Spuštěí ingestion pipeline (znalostní báze)."""
from __future__ import annotations

import asyncio
import sys

from src.knowledge.ingestion import IngestionPipeline
from src.knowledge.anonymization import Anonymizer


async def main() -> None:
    pipeline = IngestionPipeline(anonymizer=Anonymizer())
    # Placeholder – v plné implementaci se načtou dokumenty ze scripts/ingestion/
    print("Ingestion pipeline připraven. Žádné dokumenty ke zpracování.")


if __name__ == "__main__":
    asyncio.run(main())