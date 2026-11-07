"""Endpointy pro Quant Engine (ROI, citlivost, simulace)."""
from __future__ import annotations

from fastapi import APIRouter

from src.quant.assumption_graph import AssumptionGraph
from src.quant.engine import QuantEngine
from src.quant.monte_carlo import MonteCarlo
from src.quant.sensitivity import SensitivityAnalyzer

router = APIRouter()

_engine = QuantEngine()
_sensitivity = SensitivityAnalyzer(engine=_engine)
_monte_carlo = MonteCarlo(engine=_engine)
_assumption_graph = AssumptionGraph()


@router.post("/roi")
async def compute_roi(payload: dict) -> dict:
    """Vypočítá deterministický ROI (nikoli LLM-generated)."""
    return _engine.compute_roi(payload)


@router.post("/sensitivity")
async def sensitivity(payload: dict) -> dict:
    """Citlivostní analýza pro změny předpokladů."""
    base_case = payload.get("base_case", {})
    variations = payload.get("variations", [])
    results = _sensitivity.analyze(base_case=base_case, variations=variations)
    return {"base_case": base_case, "results": results, "status": "ok"}


@router.post("/monte-carlo")
async def monte_carlo(payload: dict) -> dict:
    """Monte Carlo simulace pro odhad distribuce výsledků."""
    model = payload.get("model", {})
    iterations = int(payload.get("iterations", 1000))
    seed = payload.get("seed")
    return _monte_carlo.simulate(model=model, iterations=iterations, seed=seed)


@router.post("/assumptions/{assumption_id}/recompute")
async def recompute_assumption(assumption_id: str, payload: dict) -> dict:
    """Změní hodnotu předpokladu a vrátí ovlivněné větve."""
    new_value = payload.get("new_value")
    return _assumption_graph.recompute(assumption_id=assumption_id, new_value=new_value)


@router.post("/assumptions")
async def add_assumption(payload: dict) -> dict:
    """Registruje nový předpoklad do grafu."""
    assumption_id = payload.get("assumption_id")
    value = payload.get("value")
    depends_on = payload.get("depends_on", [])
    _assumption_graph.add_assumption(assumption_id=assumption_id, value=value, depends_on=depends_on)
    return {"assumption_id": assumption_id, "status": "registered"}