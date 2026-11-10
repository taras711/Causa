"""Evaluační testy: čísla ve zlatých A3 případech musí pocházet z deterministického
Quant Enginu, nikoliv být vymyšlena LLM. Porovnání s silnějším modelem probíhá jen
jako měřítko stropu kvality a pouze nad anonymizovanými daty (tady jsou případy
anonymizované, žádná důvěrná data klienta).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.quant.confidence import ConfidenceCalculator
from src.quant.engine import QuantEngine
from tests.eval.golden_cases import get_golden_cases


def test_every_golden_case_has_deterministic_quant_inputs() -> None:
    """Každý zlatý případ musí mít v kontextu quant_inputs pro Quant Engine."""
    engine = QuantEngine()
    for case in get_golden_cases():
        q = case.context.get("quant_inputs")
        assert q is not None, f"{case.case_id}: chybí quant_inputs"
        assert set(q) >= {"investment", "annual_return", "years", "discount_rate"}
        result = engine.compute_roi(q)
        assert result["status"] == "ok"
        assert result["roi"] is not None


def test_quant_deterministic_same_inputs_same_output() -> None:
    engine = QuantEngine()
    q = {"investment": 100000, "annual_return": 30000, "years": 5, "discount_rate": 0.08}
    assert engine.compute_roi(q) == engine.compute_roi(q)


def test_confidence_is_not_llm_self_assessment() -> None:
    """Confidence počítané ze claimů nemůže být libovolné LLM číslo."""
    calc = ConfidenceCalculator()
    claims = [
        {"id": 1, "source": "assumption", "assumption": True},
    ]
    comps = ConfidenceCalculator.from_claims(claims, levels=["unverified"])
    scored = calc.score(comps)
    assert scored["confidence"] < 0.5  # slabý zdroj + neověřeno = nízká confidence
    assert scored["calibrated"] is False


@pytest.mark.asyncio
async def test_golden_case_roi_comes_from_quant_engine() -> None:
    """SolutionDesigner nevrací LLM-odhad estimated_roi, ale výsledek Quant Enginu."""
    from src.agents.solution_designer import SolutionDesignerAgent, SolutionDesignerInput

    agent = SolutionDesignerAgent()
    case = get_golden_cases()[0]
    q = case.context["quant_inputs"]
    expected = QuantEngine().compute_roi(q)

    with patch.object(
        agent,
        "_call_ollama_json",
        new_callable=AsyncMock,
        return_value={"solutions": [{"name": "Řešení A", "steps": ["krok 1"]}]},
    ):
        result = await agent.run(
            SolutionDesignerInput(
                root_causes=["Příčina A"],
                claims=case.claims,
                verification_levels=["verified", "partial", "unverified"],
                agreement=0.6,
                quant_inputs=q,
            )
        )

    assert result.estimated_roi == expected["roi"]
    assert result.quant_result is not None
    assert result.quant_result["status"] == "ok"
    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence_basis is not None
    assert result.confidence_basis["calibrated"] is False


@pytest.mark.asyncio
async def test_no_quant_inputs_means_no_estimated_roi() -> None:
    """Bez explicitních vstupů (data klienta / předpoklad) nesmí být estimated_roi."""
    from src.agents.solution_designer import SolutionDesignerAgent, SolutionDesignerInput

    agent = SolutionDesignerAgent()
    with patch.object(
        agent,
        "_call_ollama_json",
        new_callable=AsyncMock,
        return_value={
            "solutions": [{"name": "Řešení A", "steps": ["krok 1"]}],
            "estimated_roi": 99.0,  # LLM by chtělo vymyslet číslo — musí být ignorováno
        },
    ):
        result = await agent.run(
            SolutionDesignerInput(root_causes=["Příčina A"], claims=[])
        )

    assert result.estimated_roi is None
    assert result.quant_result is None