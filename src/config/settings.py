"""Pydantic settings – čte z .env a proměnných prostředí."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"
    log_level: str = "INFO"
    secret_key: str = "change-in-production"

    database_url: str = "sqlite:///./data/sqlite/causa.db"

    ollama_base_url: str = "http://localhost:11434"
    model_small: str = "qwen2.5:3b"
    model_large: str = "qwen2.5:14b"
    model_embedding: str = "nomic-embed-text"

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