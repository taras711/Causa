"""Základní třída agenta se schématem, nástroji a úrovní autonomie L0–L3."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class AutonomyLevel(str, Enum):
    L0 = "L0"  # člověk rozhoduje, agent jen navrhuje
    L1 = "L1"  # agent navrhuje, člověk schvaluje
    L2 = "L2"  # agent provádí s dohledem člověka
    L3 = "L3"  # plná autonomie v definovaných mezích


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Základní třída pro všechny typované agenty."""

    def __init__(
        self,
        name: str,
        autonomy: AutonomyLevel = AutonomyLevel.L1,
        input_schema: type[BaseModel] | None = None,
        output_schema: type[BaseModel] | None = None,
    ) -> None:
        self.name = name
        self.autonomy = autonomy
        self.input_schema = input_schema
        self.output_schema = output_schema

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