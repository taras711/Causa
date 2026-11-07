"""Unit testy pro Settings (načtení modelové konfigurace z configs/models.yaml)."""

from __future__ import annotations

from src.config.settings import Settings


def test_settings_loads_model_names_from_yaml() -> None:
    settings = Settings()
    assert settings.model_small == "qwen3.5:4b"
    assert settings.model_large == "qwen3:14b"
    assert settings.model_complex == "hf.co/Qwen/Qwen3-14B-GGUF:Q5_K_M"
    assert settings.model_embedding == "nomic-embed-text"


def test_settings_has_expected_defaults() -> None:
    settings = Settings()
    assert settings.env == "dev"
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.database_url == "sqlite:///./data/sqlite/causa.db"


def test_settings_model_properties_return_strings() -> None:
    settings = Settings()
    for role in ("small", "large", "complex", "embedding"):
        value = getattr(settings, f"model_{role}")
        assert isinstance(value, str)
        assert len(value) > 0