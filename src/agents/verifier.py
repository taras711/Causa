"""Verifier – ověření tvrzení proti důkazům, datům klienta nebo předpokladům."""
from __future__ import annotations

from pydantic import BaseModel, Field


class VerifierInput(BaseModel):
    claim_text: str
    source: str  # work_model | client_data | assumption
    evidence: str | None = None


class VerifierOutput(BaseModel):
    verified: bool
    verification_level: str = Field(..., description="unverified | partial | verified")
    notes: str = ""