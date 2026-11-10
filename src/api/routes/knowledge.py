"""Endpointy pro znalostní bázi, FaceModel, retrieval."""
from __future__ import annotations

from fastapi import APIRouter

from src.knowledge.ingestion import IngestionPipeline
from src.knowledge.retrieval import HybridRetriever
from src.knowledge.verification import VerificationLayer

router = APIRouter()

_retriever = HybridRetriever()
_ingestion = IngestionPipeline(retriever=_retriever)
_verifier = VerificationLayer()


@router.get("/")
async def list_knowledge() -> dict[str, list]:
    return {"records": _retriever.get_all()}


@router.post("/search")
async def search(payload: dict) -> dict:
    query = payload.get("query", "")
    top_k = int(payload.get("top_k", 5))
    results = _retriever.search(query=query, top_k=top_k)
    return {"query": query, "results": results, "count": len(results)}


@router.post("/ingest")
async def ingest(payload: dict) -> dict:
    result = await _ingestion.ingest(payload)
    return result


@router.post("/verify")
async def verify(payload: dict) -> dict:
    result = _verifier.verify(payload)
    return result