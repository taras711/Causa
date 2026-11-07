"""Evidence Retriever – vyhledávání v znalostní bázi a datech klienta."""
from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceRetrieverInput(BaseModel):
    query: str = Field(..., description="Vyhledávací dotaz")
    tenant_id: str = "default"
    top_k: int = Field(5, ge=1, le=20)


class EvidenceRetrieverOutput(BaseModel):
    results: list[dict] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)