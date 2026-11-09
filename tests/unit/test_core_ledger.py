"""Unit testy pro core/ledger.py — append-only auditní ledger."""

from __future__ import annotations

import os
import tempfile

from src.core.ledger import Ledger


def _temp_ledger() -> tuple[Ledger, str]:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return Ledger(db_path=path), path


def test_ledger_append_and_get_for_case() -> None:
    ledger, path = _temp_ledger()
    try:
        ledger.append(event="case_created", case_id="case-1", step="init")
        ledger.append(event="step_started", case_id="case-1", step="framer")
        ledger.append(event="step_completed", case_id="case-1", step="framer")
        ledger.append(event="other", case_id="case-2", step="init")

        entries = ledger.get_for_case("case-1")
        assert len(entries) == 3
        assert entries[0]["event"] == "case_created"
        assert entries[1]["event"] == "step_started"
        assert entries[2]["event"] == "step_completed"
        assert all(e["case_id"] == "case-1" for e in entries)

        entries_case2 = ledger.get_for_case("case-2")
        assert len(entries_case2) == 1
    finally:
        os.unlink(path)


def test_ledger_detail_json() -> None:
    ledger, path = _temp_ledger()
    try:
        ledger.append(
            event="step_completed",
            case_id="case-1",
            step="diagnostician",
            detail={"root_causes": ["unclear requirements"], "confidence": 0.8},
        )
        entries = ledger.get_for_case("case-1")
        assert entries[0]["detail"]["root_causes"] == ["unclear requirements"]
        assert entries[0]["detail"]["confidence"] == 0.8
    finally:
        os.unlink(path)


def test_ledger_empty_case() -> None:
    ledger, path = _temp_ledger()
    try:
        assert ledger.get_for_case("nonexistent") == []
    finally:
        os.unlink(path)
