"""Endpointy pro spouštění agentů a seznam agentů."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path

from src.agents.diagnostician import DiagnosticianAgent
from src.agents.evidence_retriever import EvidenceRetrieverAgent
from src.agents.framer import FramerAgent
from src.agents.solution_designer import SolutionDesignerAgent
from src.agents.verifier import VerifierAgent
from src.knowledge.retrieval import HybridRetriever

router = APIRouter()

# Inicializace agentů (v produkcji by se načetli z konfigurace)
_retriever = HybridRetriever()
_agents = {
    "framer": FramerAgent(),
    "diagnostician": DiagnosticianAgent(),
    "evidence_retriever": EvidenceRetrieverAgent(retriever=_retriever),
    "solution_designer": SolutionDesignerAgent(),
    "verifier": VerifierAgent(),
}


@router.get("/")
async def list_agents() -> dict[str, list]:
    return {
        "agents": [
            {
                "name": name,
                "autonomy": agent.autonomy.value,
                "model": agent.model_name,
            }
            for name, agent in _agents.items()
        ]
    }


@router.post("/{agent_name}/run")
async def run_agent(
    agent_name: str = Path(..., description="Název agenta (framer, diagnostician, ...)"),
    payload: dict = {},
) -> dict:
    if agent_name not in _agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' neexistuje")

    agent = _agents[agent_name]
    try:
        validated_input = agent.validate_input(payload)
        result = await agent.run(validated_input)
        output = agent.validate_output(result)
        if hasattr(output, "model_dump"):
            return output.model_dump()
        return output
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))