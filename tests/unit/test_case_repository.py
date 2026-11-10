from __future__ import annotations

from datetime import UTC, datetime

from src.core.case import Case, CaseStatus
from src.core.case_repository import CaseRepository


def test_repository_persists_case_across_repository_instances(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'cases.db'}"
    repository = CaseRepository(database_url)
    case = Case(
        case_id="case-1",
        title="Výpadky výroby",
        tenant_id="tenant-a",
        plan=["framer"],
        context={"problem_statement": "Testovací problém"},
    )
    case.status = CaseStatus.RUNNING
    case.completed_steps = ["framer"]
    case.claims = [{"id": 1, "text": "claim"}]
    case.updated_at = datetime.now(UTC)
    repository.save(case)

    restored = CaseRepository(database_url).get("case-1", tenant_id="tenant-a")

    assert restored is not None
    assert restored.title == case.title
    assert restored.status is CaseStatus.RUNNING
    assert restored.context == case.context
    assert restored.completed_steps == ["framer"]
    assert restored.claims == case.claims
    assert restored.created_at == case.created_at


def test_repository_delete_respects_tenant_filter(tmp_path) -> None:
    repository = CaseRepository(f"sqlite:///{tmp_path / 'cases.db'}")
    repository.save(Case(case_id="case-a", title="A", tenant_id="tenant-a"))
    repository.save(Case(case_id="case-b", title="B", tenant_id="tenant-b"))

    assert repository.delete("case-b", tenant_id="tenant-a") is False
    assert repository.get("case-b") is not None
    assert repository.delete("case-a", tenant_id="tenant-a") is True
    assert repository.get("case-a") is None


def test_repository_search_status_pagination_and_tenant_filter(tmp_path) -> None:
    repository = CaseRepository(f"sqlite:///{tmp_path / 'cases.db'}")
    fixed_time = datetime(2026, 1, 1, tzinfo=UTC)
    for case_id, title, tenant, status in (
        ("a", "Výroba A", "tenant-a", CaseStatus.DRAFT),
        ("b", "Výroba B", "tenant-a", CaseStatus.COMPLETED),
        ("c", "Finance C", "tenant-a", CaseStatus.DRAFT),
        ("d", "Výroba D", "tenant-b", CaseStatus.DRAFT),
        ("e", "Výroba E", "tenant-a", CaseStatus.DRAFT),
    ):
        case = Case(case_id=case_id, title=title, tenant_id=tenant)
        case.status = status
        case.created_at = fixed_time
        case.updated_at = fixed_time
        repository.save(case)

    rows, total = repository.list_cases(
        page=1, page_size=1, query="výroba", status="draft", tenant_id="tenant-a"
    )
    next_rows, next_total = repository.list_cases(
        page=2, page_size=1, query="výroba", status="draft", tenant_id="tenant-a"
    )

    assert total == next_total == 2
    assert [row["case_id"] for row in rows] == ["a"]
    assert [row["case_id"] for row in next_rows] == ["e"]
    assert repository.get("d", tenant_id="tenant-a") is None
