"""Evaluační testy nad zlatými A3 případy (tests/eval/golden_cases.py)."""

from __future__ import annotations

from tests.eval.golden_cases import get_golden_cases, get_snapshots, to_snapshot


def test_golden_cases_load_six_cases() -> None:
    cases = get_golden_cases()
    assert len(cases) == 6
    case_ids = {c.case_id for c in cases}
    assert case_ids == {f"case-00{i}-2026" for i in range(1, 7)}


def test_every_golden_case_has_quant_inputs() -> None:
    """Kazdy zvlaty pripad musi mit deterministické vstupy pro Quant Engine."""
    for case in get_golden_cases():
        q = case.context.get("quant_inputs")
        assert q is not None, f"{case.case_id}: chybí quant_inputs"
        assert set(q) >= {"investment", "annual_return", "years", "discount_rate"}


def test_golden_case_has_required_metadata() -> None:
    cases = get_golden_cases()
    for case in cases:
        assert case.case_id
        assert case.title
        assert case.tenant_id
        assert isinstance(case.context, dict)
        assert isinstance(case.plan, list)
        assert len(case.plan) > 0


def test_golden_case_claims_have_required_fields() -> None:
    cases = get_golden_cases()
    valid_sources = {"work_model", "client_data", "assumption"}
    for case in cases:
        assert len(case.claims) == 3, f"{case.case_id}: očekáváno 3 claimy"
        for claim in case.claims:
            assert "id" in claim
            assert "text" in claim
            assert claim["source"] in valid_sources
            assert "confidence" in claim
            assert "created_at" in claim
            assert "verified" in claim
            # claimy ze zdroje assumption musí mít assumption=True
            if claim["source"] == "assumption":
                assert claim["assumption"] is True


def test_golden_case_references_valid_claim_ids() -> None:
    cases = get_golden_cases()
    for case in cases:
        claim_ids = {c["id"] for c in case.claims}
        for rec in case.recommendations:
            for cid in rec["basis_claim_ids"]:
                assert cid in claim_ids, f"{case.case_id}: doporučení odkazuje na neexistující claim {cid}"


def test_golden_case_plan_contains_all_agent_steps() -> None:
    cases = get_golden_cases()
    expected_steps = {"framer", "diagnostician", "evidence_retriever", "solution_designer", "verifier"}
    for case in cases:
        plan_text = " ".join(case.plan)
        for step in expected_steps:
            assert step in plan_text, f"{case.case_id}: plán missing krok '{step}'"


def test_to_snapshot_structure() -> None:
    cases = get_golden_cases()
    snapshots = get_snapshots()
    assert len(snapshots) == len(cases)
    for snap in snapshots:
        assert set(snap.keys()) == {
            "case_id", "title", "tenant_id", "context", "plan", "claims", "recommendations"
        }


def test_to_snapshot_matches_case() -> None:
    cases = get_golden_cases()
    snapshots = {s["case_id"]: s for s in get_snapshots()}
    for case in cases:
        snap = snapshots[case.case_id]
        assert snap["title"] == case.title
        assert snap["claims"] == case.claims
        assert snap["recommendations"] == case.recommendations
