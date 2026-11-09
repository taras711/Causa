"""
Zlate A3 pripady - anonymizovane zkusebni pripady pro evaluani sadu.

Format odpovida strukture Case modelu v src/core/case.py:
- Case: case_id, title, tenant_id, plan, status, context, claims, recommendations
- Claim: id, text, source (work_model | client_data | assumption), evidence, assumption, confidence, created_at, verified
- Recommendation: id, text, basis_claim_ids, roi, confidence, created_at

Kazdy pripad obsahuje:
1. Case metadata
2. Kontext (anonymizovany)
3. Plan kroku (pipeline)
4. Claimy s povinnym zdrojem
5. Doporuceni s odkazem na claimy
"""

from __future__ import annotations

from typing import Any

THIS_YEAR = "2026"

GOLDEN_CASES: list["GoldenCase"] = []


class GoldenCase:
    def __init__(
        self,
        case_id: str,
        title: str,
        tenant_id: str = "default",
        context: dict[str, Any] | None = None,
        plan: list[str] | None = None,
    ) -> None:
        self.case_id = case_id
        self.title = title
        self.tenant_id = tenant_id
        self.context = context or {}
        self.plan = plan or []
        self.claims: list[dict[str, Any]] = []
        self.recommendations: list[dict[str, Any]] = []

    def add_claim(
        self,
        text: str,
        source: str,
        evidence: str | None = None,
        assumption: bool = False,
        confidence: float | None = None,
    ) -> dict[str, Any]:
        claim = {
            "id": len(self.claims) + 1,
            "text": text,
            "source": source,
            "evidence": evidence,
            "assumption": assumption,
            "confidence": confidence,
            "created_at": "2026-11-08T00:00:00+00:00",
            "verified": False,
        }
        self.claims.append(claim)
        return claim

    def add_recommendation(
        self,
        text: str,
        basis_claim_ids: list[int],
        roi: float | None = None,
        confidence: float | None = None,
    ) -> dict[str, Any]:
        rec = {
            "id": len(self.recommendations) + 1,
            "text": text,
            "basis_claim_ids": basis_claim_ids,
            "roi": roi,
            "confidence": confidence,
            "created_at": "2026-11-08T00:00:00+00:00",
        }
        self.recommendations.append(rec)
        return rec
def _build_case_1() -> GoldenCase:
    """Pripad 1: Produktova spolecnost - neuspesny launch zakazniku."""
    case = GoldenCase(
        case_id=f"case-001-{THIS_YEAR}",
        title="Nedostatecna uzivatelska prijatelnost noveho dashboardu",
        tenant_id="tenant-acme",
        context={
            "company_size": "200-500 zamestnancu",
            "industry": "e-commerce",
            "employee_role": "product manager",
            "problem_area": "dashboard UX, adoption",
            "timeline": "6 mesicu od launchu",
        },
        plan=[
            "framer: definice rozsahu pripadu",
            "diagnostician: analyza korenovych pricin",
            "evidence_retriever: vyhledavani v znalostni bazi",
            "solution_designer: navrh reseni",
            "verifier: overeni tvrzeni",
        ],
    )

    case.add_claim(
        text="70 % uzivatelu dashboardu nepozivaji po 30 dnech.",
        source="client_data",
        evidence="Anonymizovana data usage analytics (tenure, session count).",
        confidence=0.85,
    )
    case.add_claim(
        text="Hlavnim duvodem nizkeho vyuziti je prehnane zanoreni v navigaci.",
        source="work_model",
        evidence="Lean UX handbook, trida Figma patterns.",
        assumption=False,
    )
    case.add_claim(
        text="Castecne zmeny UI nezesly pomer uzivatelskych znamek vs. plynuleho pripojeni.",
        source="assumption",
        evidence=None,
        assumption=True,
        confidence=0.6,
    )

    case.add_recommendation(
        text="Revolucni redesign s jednoduchou navigaci a persona-driven welcome flow.",
        basis_claim_ids=[1, 2],
        roi=22.5,
        confidence=0.7,
    )
    case.add_recommendation(
        text="A/B test novych vzoru uzivatelskeho rozhrani pred plnym rollout.",
        basis_claim_ids=[1],
        roi=8.3,
        confidence=0.6,
    )

    return case
def _build_case_2() -> GoldenCase:
    """Pripad 2: Dodavatel - nespolehlive dodaci ve vite logistiky."""
    case = GoldenCase(
        case_id=f"case-002-{THIS_YEAR}",
        title="Nespolehlive dodaci lhuty u klicoveho dodavatele",
        tenant_id="tenant-logistik",
        context={
            "company_size": "100-250 zamestnancu",
            "industry": "logistics",
            "employee_role": "supply chain manager",
            "problem_area": "delivery reliability, safety stock",
            "timeline": "12 mesicu",
        },
        plan=[
            "framer: definice rozsahu pripadu",
            "diagnostician: analyza korenovych pricin",
            "evidence_retriever: vyhledavani v znalostni bazi",
            "solution_designer: navrh reseni",
            "verifier: overeni tvrzeni",
        ],
    )

    case.add_claim(
        text="25 % dodavek prichazi pozdeji nez slibenych 5 dnu mezi order a delivery.",
        source="client_data",
        evidence="ERP export dodacich lhut, anonymizovany.",
        confidence=0.9,
    )
    case.add_claim(
        text="Nejistota dokladu vede k zvysovani mnozstvi zasob o 30 %.",
        source="work_model",
        evidence="Sales & Operations Planning whitepaper.",
        assumption=False,
    )
    case.add_claim(
        text="Vyuzití prediktivni analyzy snizuje zasoby.",
        source="assumption",
        evidence=None,
        assumption=True,
        confidence=0.55,
    )

    case.add_recommendation(
        text="Zavedeni safety stock modelu na zaklade historickych distribuci.",
        basis_claim_ids=[1, 2],
        roi=15.2,
        confidence=0.65,
    )
    case.add_recommendation(
        text="Partnerstvi s vice dodavateli pro zvyseni zasobove odolnosti.",
        basis_claim_ids=[1],
        roi=5.7,
        confidence=0.55,
    )

    return case
def _build_case_3() -> GoldenCase:
    """Pripad 3: Vzdelavaci spolecnost - nedostatecna podpora zamestnancu."""
    case = GoldenCase(
        case_id=f"case-003-{THIS_YEAR}",
        title="Nizka angaovanost internych skoleni",
        tenant_id="tenant-cognit",
        context={
            "company_size": "500-2000 zamestnancu",
            "industry": "IT and consulting",
            "employee_role": "L&D manager",
            "problem_area": "learning adoption, upsell",
            "timeline": "8 mesicu",
        },
        plan=[
            "framer",
            "diagnostician",
            "evidence_retriever",
            "solution_designer",
            "verifier",
        ],
    )

    case.add_claim(
        text="Aktivni ucast na LMS byla <15 %.",
        source="client_data",
        evidence="LMS event logs, anonymizovane.",
        confidence=0.8,
    )
    case.add_claim(
        text="Shrnuti dat ukazuje, ze skoleni neni v souladu s pracovnimi scenari.",
        source="work_model",
        evidence="Industry analysis, McKinsey trendy.",
        assumption=False,
    )
    case.add_claim(
        text="Gamifikace zvysuje motivaci k ucasti.",
        source="assumption",
        evidence=None,
        assumption=True,
        confidence=0.5,
    )

    case.add_recommendation(
        text="Zmena na scenario-based learning s manager prubeznym feedbackem.",
        basis_claim_ids=[1, 2],
        roi=18.8,
        confidence=0.6,
    )
    case.add_recommendation(
        text="Pilotace skoleni v dtici skupine zamestnancu s follow-up pruzkumem.",
        basis_claim_ids=[1],
        roi=6.2,
        confidence=0.5,
    )

    return case


def get_golden_cases() -> list[GoldenCase]:
    """Vrati vsechny zlaté pripady."""
    GOLDEN_CASES.clear()
    GOLDEN_CASES.append(_build_case_1())
    GOLDEN_CASES.append(_build_case_2())
    GOLDEN_CASES.append(_build_case_3())
    return GOLDEN_CASES


def to_snapshot(case: GoldenCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "title": case.title,
        "tenant_id": case.tenant_id,
        "context": case.context,
        "plan": case.plan,
        "claims": case.claims,
        "recommendations": case.recommendations,
    }


def get_snapshots() -> list[dict[str, Any]]:
    return [to_snapshot(c) for c in get_golden_cases()]


if __name__ == "__main__":
    import json

    for snapshot in get_snapshots():
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        print("-" * 60)
