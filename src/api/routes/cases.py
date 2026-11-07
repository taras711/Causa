"""Endpointy pro správu případů (vytvoření, stav, výsledek)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_cases() -> dict[str, list]:
    return {"cases": []}


@router.post("/")
async def create_case(payload: dict) -> dict:
    return {"case_id": "placeholder", "status": "draft"}


@router.get("/{case_id}")
async def get_case(case_id: str) -> dict:
    return {"case_id": case_id, "status": "not_implemented"}