#!/usr/bin/env python3
"""Migrace databázového schématu (spustí se automaticky při startu)."""
from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    db_path = Path("data/sqlite/causa.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT '[]',
                completed_steps TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event TEXT NOT NULL,
                case_id TEXT,
                step TEXT,
                detail TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ledger_case ON ledger(case_id)"
        )
        conn.commit()
        print("Databázové schéma připraveno.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()