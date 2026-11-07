"""Model případu (Case), jeho životní cyklus a kroky."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CaseStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class CaseStep:
    """Jeden krok v pracovním toku případu."""

    def __init__(
        self,
        step_name: str,
        status: str = "pending",
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        self.step_name = step_name
        self.status = status
        self.started_at = started_at
        self.completed_at = completed_at
        self.result = result
        self.error = error


class Case:
    """Případ (A3 analýza) se stavem, plánem kroků a stopou původu."""

    def __init__(
        self,
        case_id: str,
        title: str,
        tenant_id: str = "default",
        plan: list[str] | None = None,
        status: CaseStatus = CaseStatus.DRAFT,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.case_id = case_id
        self.title = title
        self.tenant_id = tenant_id
        self.plan = plan or []
        self.status = status
        self.context = context or {}
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.steps: list[CaseStep] = []
        self.completed_steps: list[str] = []
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
        """Přidá tvrzení (claim) s povinným zdrojem a stopou původu."""
        claim = {
            "id": len(self.claims) + 1,
            "text": text,
            "source": source,  # work_model | client_data | assumption
            "evidence": evidence,
            "assumption": assumption,
            "confidence": confidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
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
        """Přidá doporučení s odkazem na podkladová tvrzení."""
        rec = {
            "id": len(self.recommendations) + 1,
            "text": text,
            "basis_claim_ids": basis_claim_ids,
            "roi": roi,
            "confidence": confidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.recommendations.append(rec)
        return rec