#!/usr/bin/env python3
"""Anonymizace dat klienta před uložením."""
from __future__ import annotations

from src.knowledge.anonymization import Anonymizer


def main() -> None:
    anonymizer = Anonymizer()
    print("Anonymizační modul připraven.")


if __name__ == "__main__":
    main()