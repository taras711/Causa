"""Unit testy pro neměnný append-only ledger (provenance stopa)."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.core.ledger import Ledger


@pytest.fixture
def ledger_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def ledger(ledger_path: str) -> Ledger:
    return Ledger(db_path=ledger_path)


def test_ledger_creates_table_on_init(ledger: Ledger, ledger_path: str) -> None:
    import sqlite3

    conn = sqlite3.connect(ledger_path)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ledger'"
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 1


def test_ledger_append_returns_id(ledger: Ledger) -> None:
    record_id = ledger.append(
        event="step_started",
        case_id="case-1",
        step="framer",
        detail={"started_at": "2024-01-01T00:00:00+00:00"},
    )
    assert record_id == 1


def test_ledger_append_increments_id(ledger: Ledger) -> None:
    ledger.append(event="event_a", case_id="case-1")
    record_id = ledger.append(event="event_b", case_id="case-1")
    assert record_id == 2


def test_ledger_get_for_case_returns_ordered_entries(ledger: Ledger) -> None:
    ledger.append(event="step_started", case_id="case-1", step="framer")
    ledger.append(event="step_completed", case_id="case-1", step="framer")
    ledger.append(event="step_started", case_id="case-2", step="diagnostician")

    entries = ledger.get_for_case("case-1")
    assert len(entries) == 2
    assert entries[0]["event"] == "step_started"
    assert entries[0]["step"] == "framer"
    assert entries[1]["event"] == "step_completed"
    assert entries[1]["step"] == "framer"

    entries_case2 = ledger.get_for_case("case-2")
    assert len(entries_case2) == 1
    assert entries_case2[0]["case_id"] == "case-2"


def test_ledger_get_for_unknown_case_returns_empty(ledger: Ledger) -> None:
    entries = ledger.get_for_case("nonexistent")
    assert entries == []


def test_ledger_detail_is_serialized_as_json(ledger: Ledger) -> None:
    ledger.append(
        event="test_event",
        case_id="case-1",
        detail={"key": "value", "number": 42},
    )
    entries = ledger.get_for_case("case-1")
    assert entries[0]["detail"] == {"key": "value", "number": 42}


def test_ledger_detail_defaults_to_empty_dict(ledger: Ledger) -> None:
    ledger.append(event="bare_event", case_id="case-1")
    entries = ledger.get_for_case("case-1")
    assert entries[0]["detail"] == {}