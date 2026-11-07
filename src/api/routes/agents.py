"""Endpointy pro spouštění agentů a seznam agentů."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_agents() -> dict[str, list]:
    return {"agents": []}


@router.post("/{agent_name}/run")
async def run_agent(agent_name: str, payload: dict) -> dict:
    return {"agent": agent_name, "status": "not_implemented"}