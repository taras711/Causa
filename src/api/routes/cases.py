"""Endpointy pro správu případů (vytvoření, stav, výsledek, ledger)."""
from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path as FSPath
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from fastapi import Path as FastAPIPath

from src.config.settings import Settings
from src.core.case import Case, CaseStatus
from src.core.case_repository import CaseRepository
from src.core.engine import WorkflowEngine
from src.core.ledger import Ledger
from src.models.case import CaseCreate, CaseResponse
from src.utils.logging import setup_logging

setup_logging()

router = APIRouter()

_engines: dict[str, WorkflowEngine] = {}
_ledgers: dict[str, Ledger] = {}

DATA_DIR = FSPath(os.environ.get("CAUSA_DATA_DIR", "./data"))
DB_PATH = DATA_DIR / "sqlite" / "causa.db"
LEDGER_PATH = DATA_DIR / "ledger" / "ledger.db"
_settings = Settings()
_case_repository = CaseRepository(_settings.database_url)



def _get_engine(case: Case) -> WorkflowEngine:
    if case.case_id not in _engines:
        _engines[case.case_id] = WorkflowEngine(db_path=DB_PATH, ledger=_get_ledger())
    return _engines[case.case_id]


def _get_ledger() -> Ledger:
    if "default" not in _ledgers:
        _ledgers["default"] = Ledger(db_path=LEDGER_PATH)
    return _ledgers["default"]


@router.get("/")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, max_length=200),
    status: str | None = Query(None),
) -> dict:
    """Vrátí stránkovaný seznam případů s volitelným hledáním a filtrem stavu."""
    if status is not None and status not in {item.value for item in CaseStatus}:
        raise HTTPException(status_code=422, detail="Neplatný stav případu")
    records, total = _case_repository.list_cases(
        page=page,
        page_size=page_size,
        query=q,
        status=status,
        tenant_id=_settings.tenant_id,
    )
    cases = [
        {
            "case_id": row["case_id"],
            "title": row["title"],
            "tenant_id": row["tenant_id"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }
        for row in records
    ]
    return {"cases": cases, "page": page, "page_size": page_size, "total": total}


@router.post("/")
async def create_case(payload: CaseCreate) -> CaseResponse:
    case = Case(
        case_id=str(uuid4()),
        title=payload.title,
        tenant_id=_settings.tenant_id,
        plan=payload.plan,
        context=payload.context,
    )
    _case_repository.save(case)
    return CaseResponse(
        case_id=case.case_id,
        title=case.title,
        tenant_id=case.tenant_id,
        context=case.context,
        status=case.status.value,
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


@router.get("/{case_id}")
async def get_case(case_id: str = FastAPIPath(..., description="ID případu")) -> dict:
    case = _case_repository.get(case_id, tenant_id=_settings.tenant_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    return {
        "case_id": case.case_id,
        "title": case.title,
        "tenant_id": case.tenant_id,
        "context": case.context,
        "status": case.status.value,
        "plan": case.plan,
        "completed_steps": case.completed_steps,
        "claims": case.claims,
        "recommendations": case.recommendations,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
    }


@router.patch("/{case_id}")
async def update_case(
    payload: dict,
    case_id: str = FastAPIPath(..., description="ID případu"),
) -> dict:
    """Upraví název a původní vstupy případu bez přepsání výstupů A3."""
    case = _case_repository.get(case_id, tenant_id=_settings.tenant_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    if not payload or set(payload) - {"title", "context"}:
        raise HTTPException(status_code=400, detail="Neplatná pole případu")

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            raise HTTPException(status_code=422, detail="Název případu nesmí být prázdný")
        case.title = payload["title"].strip()

    if "context" in payload:
        context = payload["context"]
        editable_keys = {
            "problem_statement", "desired_outcome", "current_state", "scope", "impact",
            "timeframe", "evidence_notes", "previous_attempts", "constraints", "success_criteria",
        }
        if not isinstance(context, dict) or set(context) - editable_keys:
            raise HTTPException(status_code=400, detail="Neplatná vstupní pole případu")
        case.context = {**case.context, **context}

    case.updated_at = datetime.now(UTC)
    _case_repository.save(case)
    return {"case_id": case.case_id, "title": case.title, "context": case.context}


@router.delete("/{case_id}", status_code=204)
async def delete_case(case_id: str = FastAPIPath(..., description="ID případu")) -> None:
    """Odstraní případ aktuálního tenanta; auditní ledger zůstává zachován."""
    case = _case_repository.get(case_id, tenant_id=_settings.tenant_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    if case.status is CaseStatus.RUNNING:
        raise HTTPException(status_code=409, detail="Běžící případ nelze odstranit")
    _case_repository.delete(case_id, tenant_id=_settings.tenant_id)
    _engines.pop(case_id, None)


@router.patch("/{case_id}/context")
async def update_case_context(
    payload: dict,
    case_id: str = FastAPIPath(..., description="ID případu"),
) -> dict:
    """Aktualizuje pouze kontext případu; ostatní metadata zůstanou beze změny."""
    case = _case_repository.get(case_id, tenant_id=_settings.tenant_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    allowed_keys = {"framing", "evidence", "diagnosis", "solution"}
    if not payload or set(payload) - allowed_keys:
        raise HTTPException(status_code=400, detail="Neplatná pole kontextu A3")
    case.context = {**case.context, **payload}
    case.updated_at = datetime.now(UTC)
    _case_repository.save(case)
    return {"case_id": case.case_id, "context": case.context}


@router.post("/{case_id}/run")
async def run_case(case_id: str = FastAPIPath(..., description="ID případu")) -> dict:
    case = _case_repository.get(case_id, tenant_id=_settings.tenant_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    case.status = CaseStatus.RUNNING
    case.updated_at = datetime.now(UTC)
    _case_repository.save(case)
    engine = _get_engine(case)
    try:
        case = engine.run_case(case)
        case.updated_at = datetime.now(UTC)
        _case_repository.save(case)
        return {
            "case_id": case.case_id,
            "status": case.status.value,
            "completed_steps": case.completed_steps,
        }
    except Exception as exc:
        case.status = CaseStatus.FAILED
        case.updated_at = datetime.now(UTC)
        _case_repository.save(case)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{case_id}/ledger")
async def get_case_ledger(case_id: str = FastAPIPath(..., description="ID případu")) -> dict:
    if _case_repository.get(case_id, tenant_id=_settings.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    ledger = _get_ledger()
    entries = ledger.get_for_case(case_id)
    return {"case_id": case_id, "entries": entries}