"""Unit testy pro src/agents/opponent.py — Devil's Advocate pravidlová kontrola."""

from __future__ import annotations

from src.agents.opponent import OpponentAgent, OpponentInput


def test_opponent_blocks_missing_source() -> None:
    agent = OpponentAgent()
    inp = OpponentInput(
        case_id="case-x",
        claims=[{"id": 1, "text": "Nějaké tvrzení bez platného zdroje", "source": "neplatny"}],
    )
    out = agent.run(inp)
    assert out.blocked is True
    assert any(f.code == "missing_source" for f in out.findings)
    assert any(f.severity == "critical" for f in out.findings)


def test_opponent_flags_unverified_number() -> None:
    agent = OpponentAgent()
    inp = OpponentInput(
        case_id="case-x",
        agent_outputs={"solution_designer": {"estimated_roi": 45.0, "confidence": 0.85}},
    )
    out = agent.run(inp)
    assert any(f.code == "unverified_number" for f in out.findings)
    assert any(f.severity == "high" for f in out.findings)


def test_opponent_accepts_quant_result() -> None:
    agent = OpponentAgent()
    inp = OpponentInput(
        case_id="case-x",
        agent_outputs={
            "solution_designer": {
                "estimated_roi": 22.5,
                "quant_result": {"status": "ok", "roi": 22.5},
            }
        },
    )
    out = agent.run(inp)
    assert not any(f.code == "unverified_number" for f in out.findings)


def test_opponent_flags_broken_references() -> None:
    agent = OpponentAgent()
    inp = OpponentInput(
        case_id="case-x",
        claims=[{"id": 1, "text": "Tvrzení A", "source": "client_data", "evidence": "e"}],
        recommendations=[
            {"text": "Řešení", "basis_claim_ids": [1, 99], "confidence": 0.8}
        ],
    )
    out = agent.run(inp)
    assert any(f.code == "broken_reference" for f in out.findings)
    assert out.blocked is True


def test_opponent_flags_assumption_based_high_confidence() -> None:
    agent = OpponentAgent()
    inp = OpponentInput(
        case_id="case-x",
        claims=[
            {"id": 1, "text": "Předpoklad A", "source": "assumption", "assumption": True},
        ],
        recommendations=[
            {"text": "Řešení na předpokladu", "basis_claim_ids": [1], "confidence": 0.8}
        ],
    )
    out = agent.run(inp)
    assert any(f.code == "assumption_based_recommendation" for f in out.findings)
    assert out.blocked is False


def test_opponent_clean_output_no_findings() -> None:
    agent = OpponentAgent()
    inp = OpponentInput(
        case_id="case-x",
        claims=[{"id": 1, "text": "Tvrzení", "source": "client_data", "evidence": "e"}],
        agent_outputs={
            "solution_designer": {
                "estimated_roi": 10.0,
                "quant_result": {"status": "ok", "roi": 10.0},
            }
        },
        recommendations=[{"text": "Řešení", "basis_claim_ids": [1], "confidence": 0.5}],
    )
    out = agent.run(inp)
    assert out.findings == []
    assert out.blocked is False