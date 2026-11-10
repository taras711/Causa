"""Unit testy pro agents/diagnostician.py — Pydantic schemata a validace."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.agents.diagnostician import (
    DiagnosticianAgent,
    DiagnosticianInput,
    DiagnosticianOutput,
)


def test_diagnostician_input_schema() -> None:
    data = DiagnosticianInput(
        scope="Analyza odchodu",
        evidence=["70 % uzivatelu odchazi po 30 dnech"],
    )
    assert data.scope == "Analyza odchodu"
    assert len(data.evidence) == 1


def test_diagnostician_output_schema_defaults() -> None:
    data = DiagnosticianOutput(
        root_causes=["Prehledna navigace chybi"],
    )
    assert data.root_causes == ["Prehledna navigace chybi"]
    assert data.contributing_factors == []
    assert data.confidence == 0.5


def test_diagnostician_agent_defaults() -> None:
    agent = DiagnosticianAgent()
    assert agent.name == "Diagnostician"
    assert agent.autonomy.value == "L1"
    assert agent.model_name == "qwen3:14b"


def test_diagnostician_confidence_out_of_range_raises() -> None:
    # Pydantic v2 vyhodi ValidationError mimo rozsah 0-1 (ge/le)
    with pytest.raises(ValidationError):
        DiagnosticianOutput(
            root_causes=["Test"],
            confidence=1.5,
        )

    with pytest.raises(ValidationError):
        DiagnosticianOutput(
            root_causes=["Test"],
            confidence=-0.5,
        )
