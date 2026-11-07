"""Model tvrzení (Claim) se stopou původu a verifikací."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClaimBase(BaseModel):
    text: str
    source: str  # work_model | client_data | assumption
    evidence: str | None = None
    assumption: bool = False
    confidence: float | None = Field(None, ge=0.0, le=1.0)


class ClaimCreate(ClaimBase):
    case_id: UUID


class ClaimResponse(ClaimBase):
    claim_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.now)