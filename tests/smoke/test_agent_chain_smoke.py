"""Kouřový (end-to-end) test celého řetězce agentů proti živému Ollama modelu.

Řetězec: Framer (qwen3.5:4b) → Diagnostician (qwen3:14b) → SolutionDesigner (qwen3:14b) → Verifier (qwen3:14b)

Vyžaduje spuštěný Ollama na http://localhost:11434 a stažené modely qwen3.5:4b i qwen3:14b.
Při nedostupnosti Ollama se test přeskočí.
"""
from __future__ import annotations

import asyncio
import time

import ollama
import pytest

from src.agents.diagnostician import DiagnosticianAgent, DiagnosticianInput
from src.agents.framer import FramerAgent, FramerInput
from src.agents.solution_designer import SolutionDesignerAgent, SolutionDesignerInput
from src.agents.verifier import VerifierAgent, VerifierInput

OLLAMA_URL = "http://localhost:11434"


def _ollama_reachable() -> bool:
    try:
        ollama.Client(host=OLLAMA_URL).list()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_reachable(),
    reason="Ollama server není dostupný na http://localhost:11434",
)


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_full_agent_chain_live_ollama() -> None:
    """Celý řetězec agentů provede A3 analýzu proti živému Ollama modelu."""
    timings: dict[str, float] = {}
    outputs: dict[str, str] = {}

    # 1. Framer – malý model pro definici rozsahu (rychlý, levný)
    t0 = time.perf_counter()
    framer = FramerAgent(ollama_base_url=OLLAMA_URL)
    framer_out = await framer.run(
        FramerInput(
            case_title="Řetězový kouřový test",
            problem_statement="Vysoké režijní náklady v provozu a pomalé schvalování faktur",
            context={"industry": "e-commerce"},
        )
    )
    t_framer = time.perf_counter() - t0
    timings["framer"] = t_framer
    outputs["framer"] = (
        f"scope={framer_out.scope!r}, "
        f"a3_structure={len(framer_out.a3_structure)} fází, "
        f"key_questions={len(framer_out.key_questions)} otázek"
    )
    assert isinstance(framer_out.scope, str) and framer_out.scope
    assert isinstance(framer_out.a3_structure, list) and len(framer_out.a3_structure) >= 1

    # 2. Diagnostician – velký model pro analýzu příčin
    t0 = time.perf_counter()
    diagnostician = DiagnosticianAgent(ollama_base_url=OLLAMA_URL)
    diag_out = await diagnostician.run(
        DiagnosticianInput(
            scope=framer_out.scope,
            evidence=[
                "Režijní náklady vzrostly o 15 % meziročně",
                "Schválení faktur trvá průměrně 5 pracovních dnů",
                "Chybí automatizace sledování nákladů",
            ],
            context={"industry": "e-commerce", "framing": framer_out.scope},
        )
    )
    t_diag = time.perf_counter() - t0
    timings["diagnostician"] = t_diag
    outputs["diagnostician"] = (
        f"root_causes={len(diag_out.root_causes)}, "
        f"contributing_factors={len(diag_out.contributing_factors)}, "
        f"confidence={diag_out.confidence:.2f}"
    )
    assert isinstance(diag_out.root_causes, list) and len(diag_out.root_causes) >= 1
    assert all(isinstance(c, str) and c for c in diag_out.root_causes)
    assert 0.0 <= diag_out.confidence <= 1.0

    # 3. SolutionDesigner – velký model pro návrh řešení
    t0 = time.perf_counter()
    designer = SolutionDesignerAgent(ollama_base_url=OLLAMA_URL)
    sol_out = await designer.run(
        SolutionDesignerInput(
            root_causes=diag_out.root_causes,
            evidence=["Finanční výkaz 2024", "Procesní mapa schvalování"],
            context={"industry": "e-commerce", "diagnosis": "; ".join(diag_out.root_causes)},
        )
    )
    t_design = time.perf_counter() - t0
    timings["solution_designer"] = t_design
    outputs["solution_designer"] = (
        f"solutions={len(sol_out.solutions)}, "
        f"estimated_roi={sol_out.estimated_roi}, "
        f"confidence={sol_out.confidence:.2f}"
    )
    assert isinstance(sol_out.solutions, list) and len(sol_out.solutions) >= 1
    assert all(isinstance(s, dict) for s in sol_out.solutions)
    assert sol_out.estimated_roi is None or (0.0 <= sol_out.estimated_roi <= 100.0)
    assert 0.0 <= sol_out.confidence <= 1.0

    # 4. Verifier – velký model pro ověření klíčového tvrzení
    t0 = time.perf_counter()
    verifier = VerifierAgent(ollama_base_url=OLLAMA_URL)
    ver_out = await verifier.run(
        VerifierInput(
            claim_text="Režijní náklady vzrostly o 15 % meziročně kvůli neefektivnímu schvalování faktur",
            source="client_data",
            evidence="Finanční výkaz 2024; Procesní mapa schvalování",
        )
    )
    t_ver = time.perf_counter() - t0
    timings["verifier"] = t_ver
    outputs["verifier"] = (
        f"verified={ver_out.verified}, "
        f"level={ver_out.verification_level}, "
        f"notes={len(ver_out.notes)} znaků"
    )
    assert ver_out.verification_level in ("unverified", "partial", "verified")
    assert isinstance(ver_out.verified, bool)
    assert isinstance(ver_out.notes, str)

    total = sum(timings.values())
    print("\n" + "=" * 60)
    print("KOUŘOVÝ TEST ŘETĚZCE AGENTŮ – VÝSLEDKY")
    print("=" * 60)
    print(f"{'Krok':<20} {'Čas (s)':>10}  Výstup")
    print("-" * 60)
    for k in ("framer", "diagnostician", "solution_designer", "verifier"):
        print(f"{k:<20} {timings[k]:>10.2f}  {outputs[k]}")
    print("-" * 60)
    print(f"{'CELKEM':<20} {total:>10.2f}  sekund")
    print("=" * 60 + "\n")

    assert total < 300, f"Řetězec trval příliš dlouho: {total:.1f} s"
