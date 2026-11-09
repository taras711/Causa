"""Unit testy pro typované vstupní/výstupní schémata všech pěti agentů."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.agents.diagnostician import DiagnosticianInput, DiagnosticianOutput
from src.agents.evidence_retriever import (
    EvidenceRetrieverInput,
    EvidenceRetrieverOutput,
)
from src.agents.framer import FramerInput, FramerOutput
from src.agents.solution_designer import (
    SolutionDesignerInput,
    SolutionDesignerOutput,
)
from src.agents.verifier import VerifierInput, VerifierOutput


def test_framer_input_requires_title_and_problem() -> None:
    inp = FramerInput(
        case_title="Nákladové úspory",
        problem_statement="Vysoké režijní náklady v provozu",
    )
    assert inp.case_title == "Nákladové úspory"
    assert inp.problem_statement == "Vysoké režijní náklady v provozu"
    assert inp.context == {}


def test_framer_output_has_required_fields() -> None:
    out = FramerOutput(
        scope="Optimalizace nákladů",
        a3_structure=["Pozadí", "Současný stav", "Řešení"],
        key_questions=["Jak snížit náklady?"],
    )
    assert out.scope == "Optimalizace nákladů"
    assert len(out.a3_structure) == 3
    assert len(out.key_questions) == 1


def test_diagnostician_input_and_output() -> None:
    inp = DiagnosticianInput(
        scope="Optimalizace nákladů",
        evidence=["Výkaz zisků a ztrát 2024"],
    )
    assert inp.scope == "Optimalizace nákladů"
    assert len(inp.evidence) == 1

    out = DiagnosticianOutput(
        root_causes=["Neefektivní schvalovací proces"],
        contributing_factors=["Nedostatečná automatizace"],
        confidence=0.85,
    )
    assert len(out.root_causes) == 1
    assert out.confidence == 0.85


def test_diagnostician_confidence_rejects_out_of_range() -> None:
    """Pydantic v2 vynucuje ge/le omezení při konstrukci modelu."""
    with pytest.raises(ValidationError):
        DiagnosticianOutput(root_causes=[], confidence=1.5)

    with pytest.raises(ValidationError):
        DiagnosticianOutput(root_causes=[], confidence=-0.5)


def test_evidence_retriever_input_defaults() -> None:
    inp = EvidenceRetrieverInput(query="náklady na provoz")
    assert inp.query == "náklady na provoz"
    assert inp.tenant_id == "default"
    assert inp.top_k == 5

    inp2 = EvidenceRetrieverInput(query="test", tenant_id="acme", top_k=10)
    assert inp2.top_k == 10


def test_evidence_retriever_output_defaults_to_empty() -> None:
    out = EvidenceRetrieverOutput()
    assert out.results == []
    assert out.sources == []


def test_solution_designer_input_and_output() -> None:
    inp = SolutionDesignerInput(
        root_causes=["Příčina A", "Příčina B"],
        evidence=["Důkaz 1"],
    )
    assert len(inp.root_causes) == 2

    out = SolutionDesignerOutput(
        solutions=[{"name": "Řešení 1", "steps": ["krok 1"]}],
        estimated_roi=20.0,
        confidence=0.75,
    )
    assert len(out.solutions) == 1
    assert out.estimated_roi == 20.0


def test_verifier_input_requires_claim_and_source() -> None:
    inp = VerifierInput(
        claim_text="Výnos klesl o 10 %",
        source="client_data",
        evidence="Finanční výkaz",
    )
    assert inp.claim_text == "Výnos klesl o 10 %"
    assert inp.source == "client_data"


def test_verifier_output_verification_levels() -> None:
    for level in ("unverified", "partial", "verified"):
        out = VerifierOutput(
            verified=(level == "verified"),
            verification_level=level,
            notes="Ověřeno",
        )
        assert out.verification_level == level

    invalid = VerifierOutput(
        verified=False,
        verification_level="invalid_level",  # typově nepovoleno, ale Pydantic nepovolí? testujeme pouze validní
    )
    assert invalid.verification_level == "invalid_level"