"""WorkModel – schéma pracovního modelu firmy s procesy, rolemi a metriky."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WorkModelBase(BaseModel):
    company_id: str
    processes: list[dict[str, Any]] = Field(default_factory=list)
    roles: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)