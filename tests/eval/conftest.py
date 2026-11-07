"""Fixtures pro evaluační testy (zlaté A3 případy)."""

from __future__ import annotations

from src.core.case import Case


GOLDEN_CASES = [
    {
        "case_id": "golden-a3-001",
        "title": "Snížení režijních nákladů ve výrobě",
        "problem_statement": "Režijní náklady ve výrobě vzrostly o 15 % meziročně",
        "tenant_id": "default",
        "plan": ["framer", "diagnostician", "evidence_retriever", "solution_designer", "verifier"],
        "expected_scope": "Optimalizace režijních nákladů ve výrobě",
        "expected_root_causes_count_min": 1,
    },
    {
        "case_id": "golden-a3-002",
        "title": "Zlepšení dodací lhůty zákazníkům",
        "problem_statement": "Průměrná dodací lhůta překračuje SLA o 5 dnů",
        "tenant_id": "default",
        "plan": ["framer", "diagnostician", "solution_designer", "verifier"],
        "expected_scope": "Snížení dodací lhůty na úroveň SLA",
        "expected_root_causes_count_min": 1,
    },
]


def make_golden_case(case_data: dict) -> Case:
    """Vytvoří Case objekt ze zlatého případu."""
    return Case(
        case_id=case_data["case_id"],
        title=case_data["title"],
        tenant_id=case_data.get("tenant_id", "default"),
        plan=case_data.get("plan", []),
        context={"problem_statement": case_data["problem_statement"]},
    )