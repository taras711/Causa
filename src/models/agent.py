"""Model agenta s definicí role, schématu a úrovně autonomy."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    name: str
    role: str
    autonomy_level: str = "L1"
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    tools: list[str] = Field(default_factory=list)


class AgentResponse(AgentBase):
    agent_id: UUID = Field(default_factory=uuid4)