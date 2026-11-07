"""Pydantic modely pro případ (Case) a související entity."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CaseBase(BaseModel):
    title: str
    tenant_id: str = "default"
    context: dict[str, Any] = Field(default_factory=dict)


class CaseCreate(CaseBase):
    plan: list[str] = Field(default_factory=list)


class CaseResponse(CaseBase):
    case_id: UUID = Field(default_factory=uuid4)
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)