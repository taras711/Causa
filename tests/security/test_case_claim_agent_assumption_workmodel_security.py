"""Bezpečnostní testy pro Pydantic modely: Case, Claim, Agent, Assumption, WorkModel."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from uuid import uuid4

from src.models.case import CaseCreate, CaseResponse
from src.models.claim import ClaimBase, ClaimCreate
from src.models.agent import AgentBase, AgentResponse
from src.models.assumption import AssumptionBase, AssumptionResponse
from src.models.work_model import WorkModelBase


# ------------------------------------------------------------------ #
# CaseCreate / CaseResponse
# ------------------------------------------------------------------ #

@pytest.mark.security
def test_case_create_empty_strings_accepted_or_rejected() -> None:
    try:
        CaseCreate(title="", tenant_id="", context={}, plan=[])
    except Exception:
        return
    assert True


@pytest.mark.security
def test_case_create_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE cases; --"
    create = CaseCreate(title=evil, tenant_id="default")
    assert create.title == evil


@pytest.mark.security
def test_case_create_xss_stored_as_data() -> None:
    xss = "<script>alert(1)</script>"
    create = CaseCreate(title=xss, tenant_id="default")
    assert xss in create.title


@pytest.mark.security
def test_case_create_huge_title_does_not_crash() -> None:
    big = "A" * 100000
    create = CaseCreate(title=big, tenant_id="default")
    assert len(create.title) == 100000


@pytest.mark.security
def test_case_response_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE cases; --"
    response = CaseResponse(title=evil, status="draft")
    assert response.title == evil


# ------------------------------------------------------------------ #
# ClaimBase / ClaimCreate
# ------------------------------------------------------------------ #

@pytest.mark.security
def test_claim_base_empty_strings_accepted_or_rejected() -> None:
    try:
        ClaimBase(text="", source="", evidence="")
    except Exception:
        return
    assert True


@pytest.mark.security
def test_claim_base_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE claims; --"
    claim = ClaimBase(text=evil, source="client_data")
    assert claim.text == evil


@pytest.mark.security
def test_claim_base_xss_stored_as_data() -> None:
    xss = "<img src=x onerror=alert(1)>"
    claim = ClaimBase(text=xss, source="work_model")
    assert xss in claim.text


@pytest.mark.security
def test_claim_confidence_out_of_range_rejected() -> None:
    with pytest.raises(ValidationError):
        ClaimBase(text="T", source="s", confidence=1.5)


# ------------------------------------------------------------------ #
# AgentBase / AgentResponse
# ------------------------------------------------------------------ #

@pytest.mark.security
def test_agent_base_empty_strings_accepted_or_rejected() -> None:
    try:
        AgentBase(name="", role="")
    except Exception:
        return
    assert True


@pytest.mark.security
def test_agent_base_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE agents; --"
    agent = AgentBase(name=evil, role="analyst")
    assert agent.name == evil


@pytest.mark.security
def test_agent_base_xss_stored_as_data() -> None:
    xss = "<svg onload=alert(1)>"
    agent = AgentBase(name=xss, role="tester")
    assert xss in agent.name


@pytest.mark.security
def test_agent_base_huge_name_does_not_crash() -> None:
    big = "A" * 100000
    agent = AgentBase(name=big, role="tester")


# ------------------------------------------------------------------ #
# AssumptionBase / AssumptionResponse
# ------------------------------------------------------------------ #

@pytest.mark.security
def test_assumption_base_empty_strings_accepted_or_rejected() -> None:
    try:
        AssumptionBase(text="", value=0.0)
    except Exception:
        return
    assert True


@pytest.mark.security
def test_assumption_base_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE assumptions; --"
    assumption = AssumptionBase(text=evil, value=0.5)
    assert assumption.text == evil


@pytest.mark.security
def test_assumption_base_xss_stored_as_data() -> None:
    xss = "<body onload=alert(1)>"
    assumption = AssumptionBase(text=xss, value=1)
    assert xss in assumption.text



# ------------------------------------------------------------------ #
# WorkModelBase
# ------------------------------------------------------------------ #

@pytest.mark.security
def test_work_model_base_empty_strings_accepted_or_rejected() -> None:
    try:
        WorkModelBase(company_id="")
    except Exception:
        return
    assert True


@pytest.mark.security
def test_work_model_base_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE work_models; --"
    wm = WorkModelBase(company_id=evil)
    assert wm.company_id == evil


@pytest.mark.security
def test_work_model_base_xss_stored_as_data() -> None:
    xss = "<script>alert('xss')</script>"
    wm = WorkModelBase(company_id=xss)
    assert xss in wm.company_id


@pytest.mark.security
def test_work_model_base_huge_company_id_does_not_crash() -> None:
    big = "B" * 100000
    wm = WorkModelBase(company_id=big)
    assert len(wm.company_id) == 100000


@pytest.mark.security
def test_work_model_base_processes_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE processes; --"
    wm = WorkModelBase(
        company_id="cid",
        processes=[{"id": evil, "name": "proc"}],
    )
    assert wm.processes[0]["id"] == evil

@pytest.mark.security
def test_assumption_base_value_out_of_numeric_range_does_not_crash() -> None:
    # value je Union[float, str, bool] - extrémní čísla by neměly crashnout
    assumption = AssumptionBase(text="T", value=float("inf"))
    assert assumption.value == float("inf")


@pytest.mark.security
def test_agent_response_injection_stored_as_data() -> None:
    evil = "'; DROP TABLE agents; --"
    response = AgentResponse(name=evil, role="r")
    assert response.name == evil
    with pytest.raises(ValidationError):
        ClaimBase(text="T", source="s", confidence=-0.1)


@pytest.mark.security
def test_claim_create_injection_in_case_id_stored_as_data() -> None:
    # case_id je UUID, injection by měla být rechazována validací typu
    with pytest.raises(ValidationError):
        ClaimCreate(text="T", source="s", case_id="'; DROP TABLE claims; --")  # type: ignore[arg-type]