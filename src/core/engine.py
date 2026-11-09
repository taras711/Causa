"""Workflow engine s checkpointy a durable execution.

Každý krok případu se zaznamená do ledgeru se stavem. Po restartu může případ
pokračovat od posledního úspěšného checkpointu (durable execution).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.ledger import Ledger
from src.core.case import Case, CaseStatus, CaseStep


class WorkflowEngine:
    """Deterministický workflow engine s trvalými checkpointy."""

    def __init__(self, db_path: str | Path, ledger: Ledger) -> None:
        self.db_path = Path(db_path)
        self.ledger = ledger
        self._steps: dict[str, Callable] = {}

    def register_step(self, name: str, func: Callable) -> None:
        """Registruje krok workflow pod daným jménem."""
        self._steps[name] = func

    def run_case(self, case: Case) -> Case:
        """Spustí všechny naplánované kroky případu s checkpointy po každém kroku."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            for step_name in case.plan:
                if step_name in case.completed_steps:
                    continue  # již hotovo z předchozího běhu

                step = CaseStep(
                    step_name=step_name,
                    status="running",
                    started_at=datetime.now(timezone.utc),
                )
                case.steps.append(step)

                # Zápis checkpointu před spuštěním kroku
                self._persist_case(conn, case)
                self.ledger.append(
                    event="step_started",
                    case_id=case.case_id,
                    step=step_name,
                    detail={"started_at": step.started_at.isoformat()},
                )

                try:
                    func = self._steps[step_name]
                    result = func(case)
                    step.status = "completed"
                    step.completed_at = datetime.now(timezone.utc)
                    step.result = result
                    case.completed_steps.append(step_name)

                    # Zápis checkpointu po úspěšném kroku
                    self._persist_case(conn, case)
                    self.ledger.append(
                        event="step_completed",
                        case_id=case.case_id,
                        step=step_name,
                        detail={"result": result},
                    )
                except Exception as exc:  # noqa: BLE001
                    step.status = "failed"
                    step.error = str(exc)
                    step.completed_at = datetime.now(timezone.utc)
                    case.status = CaseStatus.FAILED
                    self._persist_case(conn, case)
                    self.ledger.append(
                        event="step_failed",
                        case_id=case.case_id,
                        step=step_name,
                        detail={"error": str(exc)},
                    )
                    raise

            case.status = CaseStatus.COMPLETED
            self._persist_case(conn, case)
        finally:
            conn.close()

        return case

    def _persist_case(self, conn: sqlite3.Connection, case: Case) -> None:
        conn.execute(
            """
            INSERT INTO cases (case_id, status, plan, completed_steps, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(case_id) DO UPDATE SET
                status=excluded.status,
                plan=excluded.plan,
                completed_steps=excluded.completed_steps,
                updated_at=excluded.updated_at
            """,
            (
                case.case_id,
                case.status.value,
                json.dumps(case.plan),
                json.dumps(case.completed_steps),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()