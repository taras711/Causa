"""SQLAlchemy persistence for cases, isolated from workflow checkpoints."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Index,
    MetaData,
    String,
    Table,
    and_,
    create_engine,
    func,
    or_,
    select,
    update,
)
from sqlalchemy.engine import Engine, make_url

from src.core.case import Case, CaseStatus

metadata = MetaData()
case_records = Table(
    "case_records",
    metadata,
    Column("case_id", String(36), primary_key=True),
    Column("title", String(500), nullable=False),
    Column("tenant_id", String(255), nullable=False, default="default"),
    Column("status", String(32), nullable=False, index=True),
    Column("plan", JSON, nullable=False),
    Column("context", JSON, nullable=False),
    Column("completed_steps", JSON, nullable=False),
    Column("claims", JSON, nullable=False),
    Column("recommendations", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Index("ix_case_records_tenant_created", "tenant_id", "created_at"),
)


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class CaseRepository:
    """Persistent case store; SQLAlchemy allows SQLite now and PostgreSQL later."""

    def __init__(self, database_url: str, engine: Engine | None = None) -> None:
        url = make_url(database_url)
        if url.get_backend_name() == "sqlite" and url.database not in (None, ":memory:"):
            Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self.engine = engine or create_engine(
            database_url,
            connect_args={"check_same_thread": False} if url.get_backend_name() == "sqlite" else {},
            pool_pre_ping=True,
        )
        metadata.create_all(self.engine)

    def save(self, case: Case) -> None:
        values = {
            "case_id": case.case_id,
            "title": case.title,
            "tenant_id": case.tenant_id,
            "status": case.status.value,
            "plan": case.plan,
            "context": case.context,
            "completed_steps": case.completed_steps,
            "claims": case.claims,
            "recommendations": case.recommendations,
            "created_at": _utc(case.created_at),
            "updated_at": _utc(case.updated_at),
        }
        with self.engine.begin() as connection:
            exists = connection.scalar(
                select(case_records.c.case_id).where(case_records.c.case_id == case.case_id)
            )
            if exists:
                statement = (
                    update(case_records)
                    .where(case_records.c.case_id == case.case_id)
                    .values(**values)
                )
                connection.execute(statement)
            else:
                connection.execute(case_records.insert().values(**values))

    def get(self, case_id: str, *, tenant_id: str | None = None) -> Case | None:
        query = select(case_records).where(case_records.c.case_id == case_id)
        if tenant_id is not None:
            query = query.where(case_records.c.tenant_id == tenant_id)
        with self.engine.connect() as connection:
            row = connection.execute(query).mappings().one_or_none()
        if row is None:
            return None
        case = Case(
            case_id=row["case_id"],
            title=row["title"],
            tenant_id=row["tenant_id"],
            plan=row["plan"],
            status=CaseStatus(row["status"]),
            context=row["context"],
        )
        case.completed_steps = row["completed_steps"] or []
        case.claims = row["claims"] or []
        case.recommendations = row["recommendations"] or []
        case.created_at = _utc(row["created_at"])
        case.updated_at = _utc(row["updated_at"])
        return case

    def delete(self, case_id: str, *, tenant_id: str | None = None) -> bool:
        """Odstraní případ; při zadání tenant_id nesáhne na data jiného tenanta."""
        from sqlalchemy import delete

        statement = delete(case_records).where(case_records.c.case_id == case_id)
        if tenant_id is not None:
            statement = statement.where(case_records.c.tenant_id == tenant_id)
        with self.engine.begin() as connection:
            result = connection.execute(statement)
        return result.rowcount > 0

    def list_cases(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        query: str | None = None,
        status: str | None = None,
        tenant_id: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        filters = []
        if query:
            pattern = f"%{query.strip()}%"
            filters.append(
                or_(
                    case_records.c.title.ilike(pattern),
                    case_records.c.case_id.ilike(pattern),
                )
            )
        if status:
            filters.append(case_records.c.status == status)
        if tenant_id:
            filters.append(case_records.c.tenant_id == tenant_id)
        where = and_(*filters) if filters else None
        with self.engine.connect() as connection:
            count_query = select(func.count()).select_from(case_records)
            rows_query = select(case_records)
            if where is not None:
                count_query = count_query.where(where)
                rows_query = rows_query.where(where)
            total = connection.scalar(count_query) or 0
            rows = connection.execute(
                rows_query.order_by(case_records.c.created_at.desc(), case_records.c.case_id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).mappings().all()
        return [dict(row) for row in rows], total
