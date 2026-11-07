"""Endpointy pro správu případů (vytvoření, stav, výsledek, ledger)."""
from __future__ import annotations

import os
from pathlib import Path as FSPath
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi import Path as FastAPIPath

from src.core.case import Case, CaseStatus
from src.core.engine import WorkflowEngine
from src.core.ledger import Ledger
from src.models.case import CaseCreate, CaseResponse
from src.utils.logging import setup_logging

setup_logging()

router = APIRouter()

# In-memory úložiště pro vývoj (v produkcji se nahradí SQLAlchemy session)
_cases: dict[str, Case] = {}
_engines: dict[str, WorkflowEngine] = {}
_ledgers: dict[str, Ledger] = {}

DATA_DIR = FSPath(os.environ.get("CAUSA_DATA_DIR", "./data"))
DB_PATH = DATA_DIR / "sqlite" / "causa.db"
LEDGER_PATH = DATA_DIR / "ledger" / "ledger.db"


def _get_engine(case: Case) -> WorkflowEngine:
    if case.case_id not in _engines:
        _engines[case.case_id] = WorkflowEngine(db_path=DB_PATH, ledger=_get_ledger())
    return _engines[case.case_id]


def _get_ledger() -> Ledger:
    if "default" not in _ledgers:
        _ledgers["default"] = Ledger(db_path=LEDGER_PATH)
    return _ledgers["default"]


@router.get("/")
async def list_cases() -> dict[str, list]:
    return {"cases": [c.case_id for c in _cases.values()]}


@router.post("/")
async def create_case(payload: CaseCreate) -> CaseResponse:
    case = Case(
        case_id=str(uuid4()),
        title=payload.title,
        tenant_id=payload.tenant_id,
        plan=payload.plan,
        context=payload.context,
    )
    _cases[case.case_id] = case
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
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    case = _cases[case_id]
    return {
        "case_id": case.case_id,
        "title": case.title,
        "tenant_id": case.tenant_id,
        "status": case.status.value,
        "plan": case.plan,
        "completed_steps": case.completed_steps,
        "claims": case.claims,
        "recommendations": case.recommendations,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
    }


@router.post("/{case_id}/run")
async def run_case(case_id: str = FastAPIPath(..., description="ID případu")) -> dict:
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    case = _cases[case_id]
    case.status = CaseStatus.RUNNING
    engine = _get_engine(case)
    try:
        case = engine.run_case(case)
        _cases[case_id] = case
        return {
            "case_id": case.case_id,
            "status": case.status.value,
            "completed_steps": case.completed_steps,
        }
    except Exception as exc:
        case.status = CaseStatus.FAILED
        _cases[case_id] = case
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{case_id}/ledger")
async def get_case_ledger(case_id: str = FastAPIPath(..., description="ID případu")) -> dict:
    if case_id not in _cases:
        raise HTTPException(status_code=404, detail="Případ nenalezen")
    ledger = _get_ledger()
    entries = ledger.get_for_case(case_id)
    return {"case_id": case_id, "entries": entries}