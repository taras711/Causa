"""Unit testy pro Pydantic modely agenta (AgentBase, AgentResponse)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from uuid import UUID

from src.models.agent import AgentBase, AgentResponse


def test_agent_base_requires_name_and_role() -> None:
    agent = AgentBase(name="Framer", role="Business Analyst")
    assert agent.name == "Framer"
    assert agent.role == "Business Analyst"
    assert agent.autonomy_level == "L1"
    assert agent.input_schema == {}
    assert agent.output_schema == {}
    assert agent.tools == []


def test_agent_base_custom_fields() -> None:
    agent = AgentBase(
        name="Diagnostician",
        role="Root Cause Analyst",
        autonomy_level="L3",
        input_schema={"scope": "str"},
        output_schema={"root_causes": "list[str]"},
        tools=["read_work_model", "search_knowledge"],
    )
    assert agent.autonomy_level == "L3"
    assert agent.input_schema == {"scope": "str"}
    assert agent.output_schema == {"root_causes": "list[str]"}
    assert agent.tools == ["read_work_model", "search_knowledge"]


def test_agent_base_name_and_role_required() -> None:
    with pytest.raises(ValidationError):
        AgentBase()  # type: ignore[call-arg]


def test_agent_response_adds_agent_id() -> None:
    agent = AgentBase(name="Test", role="Tester")
    response = AgentResponse(**agent.model_dump(exclude_unset=True))
    assert response.agent_id is not None
    assert isinstance(response.agent_id, UUID)
    assert response.name == "Test"
    assert response.role == "Tester"