"""Model Router – výběr a přepínání LLM modelů podle konfigurace.

Model je vždy konfigurace, nikdy předpoklad v kódu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelConfig:
    name: str
    role: str  # small | large | embedding
    temperature: float = 0.1
    max_tokens: int = 4096
    context_window: int = 16384
    options: dict[str, Any] = field(default_factory=dict)


class ModelRouter:
    """Drží konfiguraci modelů a vrací vhodný model podle role."""

    def __init__(self, models: dict[str, ModelConfig]) -> None:
        self._models: dict[str, ModelConfig] = dict(models)

    def get(self, role: str) -> ModelConfig:
        """Vrátí konfiguraci modelu pro danou roli (small, large, embedding)."""
        if role not in self._models:
            raise ValueError(f"Model pro roli '{role}' není v konfiguraci.")
        return self._models[role]

    def add(self, role: str, config: ModelConfig) -> None:
        self._models[role] = config

    def list_models(self) -> list[str]:
        return sorted(self._models.keys())

    def list_by_role(self, role: str) -> list[ModelConfig]:
        """Vrátí všechny modely dané role."""
        return [m for m in self._models.values() if m.role == role]