"""Oponent (Devil's Advocate) – systematicky hledá chyby ve výstupech ostatních agentů.

Pravidlo: jeden model v různých rolích sdílí stejné slepé místo (prompt-diverzita
není nezávislý názor). Oponent je pravidlová vrstva nad výstupy agentů —
nepoužívá stejného LLM pro posuzování — což snižuje riziko korelovaných chyb.

Každý nález obsahuje závažnost (low/medium/high/critical) a návrh na opravu.
Pokud je nějaký nález critical, výstup je označen jako blocked (vyžaduje
lidský dohled před pokračováním).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


VALID_SOURCES = {"work_model", "client_data", "face_model", "assumption"}
NUMERIC_FIELDS = {"estimated_roi", "confidence", "roi", "npv", "payback_years"}

_SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class OpponentFinding(BaseModel):
    agent: str = Field(..., description="Jméno agenta, jehož výstup obsahuje nález")
    field: str | None = Field(None, description="Konkrétní pole s problémem (volitelné)")
    severity: str = Field("medium", description="low | medium | high | critical")
    code: str = Field(..., description="Kód nálezu (např. unverified_number, missing_source)")
    message: str = Field(..., description="Popis nálezu v češtině")
    suggestion: str = Field(..., description="Návrh na opravu")


class OpponentInput(BaseModel):
    case_id: str
    agent_outputs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    claims: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    verification_results: list[dict[str, Any]] = Field(default_factory=list)


class OpponentOutput(BaseModel):
    findings: list[OpponentFinding] = Field(default_factory=list)
    blocked: bool = False
    summary: str = ""


class OpponentAgent:
    """Devil's Advocate: pravidlová kontrola výstupů ostatních agentů.

    Nepoužívá LLM k posuzování — jeho logika je deterministická a nezávislá
    na modelu, který vygeneroval kontrolované výstupy.
    """

    name = "Oponent"

    def run(self, input_data: OpponentInput) -> OpponentOutput:
        findings: list[OpponentFinding] = []
        outputs = input_data.agent_outputs or {}

        # 1. Čísla bez stopy původu nesmějí být prezentována jako fakta.
        for agent_name, output in outputs.items():
            if not isinstance(output, dict):
                continue
            for field in NUMERIC_FIELDS:
                if field in output and output[field] is not None:
                    quant_ok = False
                    qr = output.get("quant_result") or {}
                    if isinstance(qr, dict) and qr.get("status") == "ok":
                        quant_ok = True
                    assumption_ok = any(
                        c.get("source") == "assumption" and c.get("assumption") is True
                        for c in (input_data.claims or [])
                    )
                    if not quant_ok and not assumption_ok:
                        findings.append(
                            OpponentFinding(
                                agent=agent_name,
                                field=field,
                                severity="high",
                                code="unverified_number",
                                message=(
                                    f"Číselná hodnota pole '{field}' u agenta "
                                    f"'{agent_name}' nemá stopu původu v Quant Enginu "
                                    f"ani explicitním předpokladu."
                                ),
                                suggestion=(
                                    "Hodnotu vypočítejte přes Quant Engine z dat klienta, "
                                    "nebo ji explicitně označte jako předpoklad."
                                ),
                            )
                        )

        # 2. Claimy bez zdroje nebo s neplatným zdrojem.
        for claim in input_data.claims or []:
            source = claim.get("source")
            if source not in VALID_SOURCES:
                findings.append(
                    OpponentFinding(
                        agent="case",
                        field=f"claim[{claim.get('id')}]",
                        severity="critical",
                        code="missing_source",
                        message=(
                            f"Tvrzení '{str(claim.get('text', ''))[:80]}...' "
                            f"nemá platný zdroj (source = {source!r})."
                        ),
                        suggestion=(
                            "Zdroj nastavte na work_model, client_data, face_model nebo assumption."
                        ),
                    )
                )
            if source == "client_data" and not claim.get("evidence"):
                findings.append(
                    OpponentFinding(
                        agent="case",
                        field=f"claim[{claim.get('id')}]",
                        severity="medium",
                        code="client_data_without_evidence",
                        message=(
                            f"Tvrzení ze zdroje client_data chybí konkrétní důkaz (evidence)."
                        ),
                        suggestion="Doplňte odkaz na konkrétní data klienta (soubor, export, metriku).",
                    )
                )

        # 3. Doporučení musí odkazovat na existující claimy.
        claim_ids = {
            c.get("id")
            for c in (input_data.claims or [])
            if c.get("id") is not None
        }
        for rec in input_data.recommendations or []:
            basis = rec.get("basis_claim_ids") or []
            missing = [cid for cid in basis if cid not in claim_ids]
            if missing:
                findings.append(
                    OpponentFinding(
                        agent="solution_designer",
                        field="basis_claim_ids",
                        severity="critical",
                        code="broken_reference",
                        message=(
                            f"Doporučení '{str(rec.get('text', ''))[:80]}...' "
                            f"odkazuje na neexistující claimy {missing}."
                        ),
                        suggestion="Odkazujte jen na existující claimy (id v Case).",
                    )
                )

        # 4. Assumption-based doporučení s vysokou confidence je rizikové.
        assumption_ids = {
            c.get("id")
            for c in (input_data.claims or [])
            if c.get("source") == "assumption" and c.get("assumption") is True
        }
        for rec in input_data.recommendations or []:
            basis = rec.get("basis_claim_ids") or []
            if basis and any(cid in assumption_ids for cid in basis):
                conf = rec.get("confidence")
                if conf is not None and float(conf) >= 0.7:
                    findings.append(
                        OpponentFinding(
                            agent="solution_designer",
                            field="confidence",
                            severity="medium",
                            code="assumption_based_recommendation",
                            message=(
                                "Doporučení je založeno na předpokladech (assumption), "
                                "nikoli na ověřených datech, přesto má vysokou confidence."
                            ),
                            suggestion="Snížte confidence nebo doporučení podložte daty klienta / WorkModelem.",
                        )
                    )

        # 5. Blokace při kritických nálezech.
        blocked = any(f.severity == "critical" for f in findings)
        findings.sort(key=lambda f: -_SEVERITY_ORDER.get(f.severity, 0))

        if blocked:
            summary = (
                "Výstup obsahuje kritické nedostatky; vyžaduje lidský dohled před pokračováním."
            )
        elif findings:
            summary = (
                "Nalezly se drobné nedostatky; doporučeno opravit před prezentací klientovi."
            )
        else:
            summary = "Nebyly zjištěny systémové nedostatky."

        return OpponentOutput(
            findings=findings,
            blocked=blocked,
            summary=summary,
        )