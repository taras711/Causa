"""Dependency injection (databáze, konfigurace, auth)."""
from __future__ import annotations

from functools import lru_cache

from src.config.settings import Settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # čte z .env / proměnných prostředí