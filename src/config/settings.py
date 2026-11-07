"""Pydantic settings – čte z .env a proměnných prostředí.

Názvy modelů pocházejí z jediného zdroje pravdy: `configs/models.yaml`.
Tento soubor již žádné hardcoded názvy modelů neobsahuje.
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


_MODELS_PATH = Path(__file__).resolve().parents[2] / "configs" / "models.yaml"


def _load_model_config() -> dict[str, str]:
    """Načte mapování role -> název modelu z configs/models.yaml."""
    import yaml  # PyYAML je projektová závislost

    with open(_MODELS_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    models = data.get("models", {})
    return {entry["role"]: entry["name"] for entry in models.values()}


class Settings(BaseSettings):
    env: str = "dev"
    log_level: str = "INFO"
    secret_key: str = "change-in-production"

    database_url: str = "sqlite:///./data/sqlite/causa.db"

    ollama_base_url: str = "http://localhost:11434"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    ui_port: int = 3000
    tenant_id: str = "default"

    backup_dir: str = "./data/backups"
    backup_encryption_key: str = "change-in-production"

    prometheus_port: int = 9090

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def model_small(self) -> str:
        return _load_model_config()["small"]

    @property
    def model_large(self) -> str:
        return _load_model_config()["large"]

    @property
    def model_complex(self) -> str:
        return _load_model_config()["complex"]

    @property
    def model_embedding(self) -> str:
        return _load_model_config()["embedding"]