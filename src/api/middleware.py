"""Middleware (logging, CORS, auditní log)."""
from __future__ import annotations

from fastapi import FastAPI


def setup_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def audit_log(request, call_next):
        response = await call_next(request)
        response.headers["X-Causa-Request-ID"] = "audit-placeholder"
        return response