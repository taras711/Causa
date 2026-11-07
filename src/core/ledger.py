"""Neměnný append-only auditní záznam (ledger) pro stopu původu (provenance)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Ledger:
    """Append-only ledger ukládající všechny události systému s časovým razítkem."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        try:
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
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ledger_event ON ledger(event)"
            )
            conn.commit()
        finally:
            conn.close()

    def append(self, event: str, case_id: str | None = None,
               step: str | None = None, detail: dict[str, Any] | None = None) -> int:
        """Přidá nový záznam do ledgeru. Vrací ID záznamu."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cur = conn.execute(
                """
                INSERT INTO ledger (ts, event, case_id, step, detail)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    event,
                    case_id,
                    step,
                    json.dumps(detail or {}, ensure_ascii=False),
                ),
            )
            conn.commit()
            return cur.lastrowid or 0
        finally:
            conn.close()

    def get_for_case(self, case_id: str) -> list[dict[str, Any]]:
        """Vrátí všechny ledgerové záznamy pro daný případ."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            rows = conn.execute(
                """
                SELECT id, ts, event, case_id, step, detail
                FROM ledger WHERE case_id = ?
                ORDER BY id ASC
                """,
                (case_id,),
            ).fetchall()
            return [
                {
                    "id": r[0],
                    "ts": r[1],
                    "event": r[2],
                    "case_id": r[3],
                    "step": r[4],
                    "detail": json.loads(r[5]) if r[5] else {},
                }
                for r in rows
            ]
        finally:
            conn.close()