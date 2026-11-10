"""Základní třída agenta se schématem, nástroji a úrovní autonomie L0–L3."""
from __future__ import annotations

import structlog
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from src.config.settings import Settings

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)

logger = structlog.get_logger(__name__)

_settings = Settings()


def _get_model_for_role(role: str) -> str:
    """Vrátí název modelu pro danou roli z jediného zdroje pravdy (configs/models.yaml)."""
    return {
        "small": _settings.model_small,
        "large": _settings.model_large,
        "complex": _settings.model_complex,
        "embedding": _settings.model_embedding,
    }[role]


class AutonomyLevel(str, Enum):
    L0 = "L0"  # člověk rozhoduje, agent jen navrhuje
    L1 = "L1"  # agent navrhuje, člověk schvaluje
    L2 = "L2"  # agent provádí s dohledem člověka
    L3 = "L3"  # plná autonomie v definovaných mezích


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Základní třída pro všechny typované agenty.

    Poskytuje společné rozhraní pro volání LLM přes Ollama,
    validaci vstupu/výstupu a strukturované logování.

    Název modelu se risolvuje z `configs/models.yaml` přes `Settings`,
    pokud není předán přímo pomocí `model_name`.
    """

    def __init__(
        self,
        name: str,
        autonomy: AutonomyLevel = AutonomyLevel.L1,
        input_schema: type[BaseModel] | None = None,
        output_schema: type[BaseModel] | None = None,
        ollama_base_url: str = "http://localhost:11434",
        model_name: str | None = None,
        model_role: str = "small",
    ) -> None:
        self.name = name
        self.autonomy = autonomy
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.ollama_base_url = ollama_base_url
        self.model_name = model_name or _get_model_for_role(model_role)

    @abstractmethod
    async def run(self, input_data: InputT) -> OutputT:
        """Spustí agenta a vrátí validovaný výstup."""
        ...

    def validate_input(self, data: dict[str, Any]) -> InputT:
        if self.input_schema is None:
            return data  # type: ignore[return-value]
        return self.input_schema(**data)

    def validate_output(self, data: Any) -> OutputT:
        if self.output_schema is None:
            return data  # type: ignore[return-value]
        return self.output_schema(**data) if isinstance(data, dict) else data

    async def _call_ollama(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Zavolá Ollama LLM a vrátě textovou odpověď.

        Všimněte si: LLM se používá jen pro generování textu/struktury,
        nikdy pro výpočet čísel (to dělá Quant Engine).
        """
        import json

        import ollama

        try:
            client = ollama.Client(host=self.ollama_base_url)
            response = client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )
            content = getattr(getattr(response, "message", None), "content", "") or ""
            logger.debug(
                "ollama_call",
                agent=self.name,
                model=self.model_name,
                prompt_len=len(user_prompt),
                response_len=len(content),
            )
            return content
        except Exception as exc:
            logger.error(
                "ollama_error",
                agent=self.name,
                model=self.model_name,
                error=str(exc),
            )
            raise

    async def _call_ollama_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Zavolá Ollama s JSON formátem odpovědi a vrátí slovník."""
        import json

        import ollama

        try:
            client = ollama.Client(host=self.ollama_base_url)
            response = client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                format="json",
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )
            content = getattr(getattr(response, "message", None), "content", "{}") or "{}"
            return json.loads(content)
        except Exception as exc:
            logger.error(
                "ollama_json_error",
                agent=self.name,
                model=self.model_name,
                error=str(exc),
            )
            raise