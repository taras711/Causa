"""Evaluační testy se zlatými A3 případy.

Tyto testy ověřují, že walking skeleton produkuje očekávanou strukturu výstupů
pro známé případy. Testy používají mocknuté Ollama volání, takže nevyžadují
spuštěný Ollama server.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.core.case import Case
from src.core.engine import WorkflowEngine
from src.core.ledger import Ledger
from src.agents.framer import FramerAgent, FramerInput
from src.agents.diagnostician import DiagnosticianAgent, DiagnosticianInput
from src.agents.solution_designer import (
    SolutionDesignerAgent,
    SolutionDesignerInput,
)
from src.agents.verifier import VerifierAgent, VerifierInput

from tests.eval.conftest import GOLDEN_CASES, make_golden_case


@pytest.fixture
def mocked_ollama_responses():
    """Vrací slovník mock odpovědí pro každého agenta."""
    return {
        "framer": {
            "scope": "Optimalizace režijních nákladů ve výrobě",
            "a3_structure": [
                "Pozadí",
                "Současný stav",
                "Kořenové příčiny",
                "Řešení",
                "Plán",
            ],
            "key_questions": [
                "Kde přesně vznikají nejvyšší náklady?",
                "Jaké procesní změny sníží režii?",
            ],
        },
        "diagnostician": {
            "root_causes": [
                "Neefektivní schvalovací proces faktur",
                "Chybějící automatizace sledování nákladů",
            ],
            "contributing_factors": ["Lidská chyba při zadávání dat"],
            "confidence": 0.85,
        },
        "solution_designer": {
            "solutions": [
                {
                    "name": "Digitální schvalovací workflow",
                    "steps": ["Výběr nástroje", "Implementace", "Školení"],
                },
                {
                    "name": "Pravidelný audit režijních nákladů",
                    "steps": ["Definice metriky", "Měsíční revize", "Reporting"],
                },
            ],
            "estimated_roi": 18.5,
            "confidence": 0.78,
        },
        "verifier": {
            "verified": True,
            "verification_level": "verified",
            "notes": "Tvrzení je podloženo daty klienta a WorkModelem.",
        },
    }


@pytest.mark.asyncio
async def test_golden_case_framer_produces_expected_scope(
    mocked_ollama_responses,
) -> None:
    """Zlatý případ 001: Framer vrátí očekávaný rozsah a strukturu A3."""
    agent = FramerAgent()
    case_data = GOLDEN_CASES[0]

    with patch.object(
        agent,
        "_call_ollama_json",
        new_callable=AsyncMock,
        return_value=mocked_ollama_responses["framer"],
    ):
        result = await agent.run(
            FramerInput(
                case_title=case_data["title"],
                problem_statement=case_data["problem_statement"],
                context={},
            )
        )

    assert result.scope == case_data["expected_scope"]
    assert len(result.a3_structure) >= 3
    assert len(result.key_questions) >= 1


@pytest.mark.asyncio
async def test_golden_case_diagnostician_produces_root_causes(
    mocked_ollama_responses,
) -> None:
    """Zlatý případ 001: Diagnostician identifikuje alespoň jednu kořenovou příčinu."""
    agent = DiagnosticianAgent()

    with patch.object(
        agent,
        "_call_ollama_json",
        new_callable=AsyncMock,
        return_value=mocked_ollama_responses["diagnostician"],
    ):
        result = await agent.run(
            DiagnosticianInput(
                scope="Optimalizace režijních nákladů ve výrobě",
                evidence=["Finanční výkaz 2024"],
            )
        )

    assert len(result.root_causes) >= 1
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.asyncio
async def test_golden_case_solution_designer_produces_solutions(
    mocked_ollama_responses,
) -> None:
    """Zlatý případ 001: Solution Designer navrhuje řešení s ROI."""
    agent = SolutionDesignerAgent()

    with patch.object(
        agent,
        "_call_ollama_json",
        new_callable=AsyncMock,
        return_value=mocked_ollama_responses["solution_designer"],
    ):
        result = await agent.run(
            SolutionDesignerInput(
                root_causes=["Neefektivní schvalovací proces"],
                evidence=["Procesní analýza"],
            )
        )

    assert len(result.solutions) >= 1
    assert result.estimated_roi is not None
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.asyncio
async def test_golden_case_verifier_confirms_claim(
    mocked_ollama_responses,
) -> None:
    """Zlatý případ 001: Verifier potvrzení tvrzení jako verified."""
    agent = VerifierAgent()

    with patch.object(
        agent,
        "_call_ollama_json",
        new_callable=AsyncMock,
        return_value=mocked_ollama_responses["verifier"],
    ):
        result = await agent.run(
            VerifierInput(
                claim_text="Režijní náklady vzrostly o 15 %",
                source="client_data",
                evidence="Finanční výkaz 2024",
            )
        )

    assert result.verified is True
    assert result.verification_level == "verified"


def test_golden_case_can_be_converted_to_case() -> None:
    """Každý zlatý případ z conftest lze převést na Case objekt."""
    for case_data in GOLDEN_CASES:
        case = make_golden_case(case_data)
        assert case.case_id == case_data["case_id"]
        assert case.title == case_data["title"]
        assert case.plan == case_data["plan"]


def test_workflow_engine_executes_golden_case_plan(tmp_path) -> None:
    """Workflow engine projde plánem zlatého případu s checkpointy."""
    db_path = str(tmp_path / "causa.db")
    ledger_path = str(tmp_path / "ledger.db")
    engine = WorkflowEngine(db_path=db_path, ledger=Ledger(db_path=ledger_path))

    executed_steps: list[str] = []

    def framer_step(case: Case) -> str:
        executed_steps.append("framer")
        case.add_claim(text="Rozsah definován", source="work_model")
        return {"scope": "test"}

    def diagnostician_step(case: Case) -> str:
        executed_steps.append("diagnostician")
        case.add_claim(text="Příčina identifikována", source="analysis")
        return {"root_causes": ["test"]}

    engine.register_step("framer", framer_step)
    engine.register_step("diagnostician", diagnostician_step)

    case = make_golden_case(GOLDEN_CASES[1])
    case.plan = ["framer", "diagnostician"]

    result = engine.run_case(case)

    assert result.status == "completed"
    assert result.completed_steps == ["framer", "diagnostician"]
    assert executed_steps == ["framer", "diagnostician"]

    entries = engine.ledger.get_for_case(case.case_id)
    events = [e["event"] for e in entries]
    assert "step_started" in events
    assert "step_completed" in events