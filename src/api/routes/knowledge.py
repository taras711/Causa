"""Endpointy pro znalostní bázi, FaceModel, retrieval."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_knowledge() -> dict[str, list]:
    return {"records": []}


@router.post("/search")
async def search(payload: dict) -> dict:
    return {"results": []}