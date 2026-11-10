from __future__ import annotations

import pytest
from fastapi import HTTPException

from src.api.routes import cases as cases_api
from src.core.case import Case, CaseStatus
from src.core.case_repository import CaseRepository
from src.models.case import CaseCreate


@pytest.mark.asyncio
async def test_cases_api_lists_paginated_filtered_tenant_data(tmp_path, monkeypatch) -> None:
    repository = CaseRepository(f"sqlite:///{tmp_path / 'api.db'}")
    monkeypatch.setattr(cases_api, "_case_repository", repository)
    monkeypatch.setattr(cases_api._settings, "tenant_id", "tenant-a")
    for case_id, title, tenant, status in (
        ("a", "Linka A", "tenant-a", CaseStatus.DRAFT),
        ("b", "Linka B", "tenant-a", CaseStatus.COMPLETED),
        ("c", "Linka C", "tenant-b", CaseStatus.DRAFT),
    ):
        case = Case(case_id=case_id, title=title, tenant_id=tenant)
        case.status = status
        repository.save(case)

    result = await cases_api.list_cases(page=1, page_size=1, q="linka", status="draft")

    assert result["total"] == 1
    assert result["page"] == 1
    assert [item["case_id"] for item in result["cases"]] == ["a"]


@pytest.mark.asyncio
async def test_cases_api_create_uses_configured_tenant_and_hides_other_tenants(
    tmp_path, monkeypatch
) -> None:
    repository = CaseRepository(f"sqlite:///{tmp_path / 'api.db'}")
    monkeypatch.setattr(cases_api, "_case_repository", repository)
    monkeypatch.setattr(cases_api._settings, "tenant_id", "tenant-a")

    created = await cases_api.create_case(
        CaseCreate(
            title="Nový případ",
            tenant_id="tenant-b",
            context={"problem_statement": "Test"},
        )
    )
    stored = repository.get(str(created.case_id))
    foreign_case = Case(case_id="foreign-case", title="Cizí případ", tenant_id="tenant-b")
    repository.save(foreign_case)

    assert created.tenant_id == "tenant-a"
    assert stored is not None and stored.tenant_id == "tenant-a"
    with pytest.raises(HTTPException) as exc_info:
        await cases_api.get_case("foreign-case")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_cases_api_can_update_inputs_and_delete_own_case(tmp_path, monkeypatch) -> None:
    repository = CaseRepository(f"sqlite:///{tmp_path / 'api.db'}")
    monkeypatch.setattr(cases_api, "_case_repository", repository)
    monkeypatch.setattr(cases_api._settings, "tenant_id", "tenant-a")
    case = Case(
        case_id="editable",
        title="Původní název",
        tenant_id="tenant-a",
        context={"problem_statement": "Původní popis", "framing": {"scope": "výstup"}},
    )
    repository.save(case)

    updated = await cases_api.update_case(
        {"title": "Nový název", "context": {"problem_statement": "Opravený popis"}},
        "editable",
    )
    stored = repository.get("editable", tenant_id="tenant-a")

    assert updated["title"] == "Nový název"
    assert stored is not None
    assert stored.context == {"problem_statement": "Opravený popis", "framing": {"scope": "výstup"}}
    assert await cases_api.delete_case("editable") is None
    assert repository.get("editable") is None


@pytest.mark.asyncio
async def test_cases_api_cannot_delete_foreign_or_running_case(tmp_path, monkeypatch) -> None:
    repository = CaseRepository(f"sqlite:///{tmp_path / 'api.db'}")
    monkeypatch.setattr(cases_api, "_case_repository", repository)
    monkeypatch.setattr(cases_api._settings, "tenant_id", "tenant-a")
    repository.save(Case(case_id="foreign", title="Cizí případ", tenant_id="tenant-b"))
    running = Case(case_id="running", title="Běžící případ", tenant_id="tenant-a")
    running.status = CaseStatus.RUNNING
    repository.save(running)

    with pytest.raises(HTTPException) as foreign_error:
        await cases_api.delete_case("foreign")
    with pytest.raises(HTTPException) as running_error:
        await cases_api.delete_case("running")

    assert foreign_error.value.status_code == 404
    assert running_error.value.status_code == 409
    assert repository.get("foreign") is not None
    assert repository.get("running") is not None


@pytest.mark.asyncio
async def test_cases_api_rejects_unknown_status(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        cases_api, "_case_repository", CaseRepository(f"sqlite:///{tmp_path / 'api.db'}")
    )

    with pytest.raises(HTTPException) as exc_info:
        await cases_api.list_cases(status="unknown")
    assert exc_info.value.status_code == 422
