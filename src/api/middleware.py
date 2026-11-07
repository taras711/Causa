"""Middleware (logging, CORS, auditní log, request ID)."""
from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.utils.logging import setup_logging


def setup_middleware(app: FastAPI) -> None:
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # v produzione omezit na konkrétní domény
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def audit_log(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Causa-Request-ID"] = request_id
        response.headers["X-Causa-Version"] = "0.1.0"
        return response