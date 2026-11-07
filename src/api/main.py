"""Vstupní bod API – inicializace FastAPI aplikace a registrace rout."""
from __future__ import annotations

from fastapi import FastAPI

from src.api.routes import agents, cases, knowledge, quant
from src.api.middleware import setup_middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="Causa API",
        description="Lokální, auditovatelná platforma pro firemní rozhodování",
        version="0.1.0",
    )
    setup_middleware(app)

    app.include_router(cases.router, prefix="/cases", tags=["cases"])
    app.include_router(agents.router, prefix="/agents", tags=["agents"])
    app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
    app.include_router(quant.router, prefix="/quant", tags=["quant"])

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()