"""Evidence Retriever – vyhledávání v znalostní bázi a datech klienta."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.agents.base import AutonomyLevel, BaseAgent


class EvidenceRetrieverInput(BaseModel):
    query: str = Field(..., description="Vyhledávací dotaz")
    tenant_id: str = "default"
    top_k: int = Field(5, ge=1, le=20)


class EvidenceRetrieverOutput(BaseModel):
    results: list[dict] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class EvidenceRetrieverAgent(BaseAgent[EvidenceRetrieverInput, EvidenceRetrieverOutput]):
    """Vyhledává relevantní důkazy v znalostní bázi a datech klienta.

    Používá malý model pro extrakci klíčových slov a HybridRetriever pro vyhledávání.
    """

    def __init__(self, retriever=None, **kwargs) -> None:
        super().__init__(
            name="EvidenceRetriever",
            autonomy=AutonomyLevel.L2,
            input_schema=EvidenceRetrieverInput,
            output_schema=EvidenceRetrieverOutput,
            model_name=kwargs.get("model_name", "qwen2.5:3b"),
            ollama_base_url=kwargs.get(
                "ollama_base_url", "http://localhost:11434"
            ),
        )
        self.retriever = retriever

    async def run(self, input_data: EvidenceRetrieverInput) -> EvidenceRetrieverOutput:
        results: list[dict] = []
        sources: list[str] = []

        if self.retriever is not None:
            results = await self.retriever.search(
                query=input_data.query, top_k=input_data.top_k
            )
            sources = [r.get("source", "neznámý") for r in results]
        else:
            # Fallback bez retrieveru – vrátí prázdné výsledky s informací
            results = []
            sources = []

        return EvidenceRetrieverOutput(results=results, sources=sources)