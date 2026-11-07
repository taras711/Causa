"""Endpointy pro Quant Engine (ROI, citlivost, simulace)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/roi")
async def compute_roi(payload: dict) -> dict:
    return {"roi": None, "status": "not_implemented"}


@router.post("/sensitivity")
async def sensitivity(payload: dict) -> dict:
    return {"results": [], "status": "not_implemented"}