"""Explicitně označený předpoklad s možností přepočtu při změně."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AssumptionBase(BaseModel):
    text: str
    value: float | str | bool
    case_id: str | None = None
    affected_branches: list[str] = Field(default_factory=list)


class AssumptionResponse(AssumptionBase):
    assumption_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)