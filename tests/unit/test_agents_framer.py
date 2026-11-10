"""Unit testy pro agents/framer.py — Pydantic schémata a validace."""

from __future__ import annotations

from src.agents.framer import FramerAgent, FramerInput, FramerOutput


def test_framer_input_schema() -> None:
    data = FramerInput(
        case_title="Testovací případ",
        problem_statement="Uživatelé odcházejí po 30 dnech",
        context={"industry": "e-commerce"},
    )
    assert data.case_title == "Testovací případ"
    assert data.context["industry"] == "e-commerce"


def test_framer_output_schema() -> None:
    data = FramerOutput(
        scope="Analýza odchodu uživatelů",
        a3_structure=["Pozadí", "Současný stav", "Kořenové příčiny", "Řešení", "Plán"],
        key_questions=["Proč odcházejí uživatelé?", "Co brání adopci?"],
    )
    assert len(data.a3_structure) == 5
    assert len(data.key_questions) == 2


def test_framer_agent_defaults() -> None:
    agent = FramerAgent()
    assert agent.name == "Framer"
    assert agent.autonomy.value == "L1"
    assert agent.model_name == "qwen3.5:4b"
    assert agent.input_schema == FramerInput
    assert agent.output_schema == FramerOutput


def test_framer_validate_input_output() -> None:
    agent = FramerAgent()
    validated = agent.validate_input(
        {
            "case_title": "Případ X",
            "problem_statement": "Popis problému",
        }
    )
    assert isinstance(validated, FramerInput)
    assert validated.case_title == "Případ X"

    output = agent.validate_output(
        {
            "scope": "Rozsah",
            "a3_structure": ["A", "B"],
            "key_questions": ["Q1"],
        }
    )
    assert isinstance(output, FramerOutput)
    assert output.scope == "Rozsah"
