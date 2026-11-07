"""Anonymizace dat klienta před uložením do znalostní báze."""
from __future__ import annotations

import re
from typing import Any


class Anonymizer:
    """Odebere nebo nahradí citlivé identifikátory v dokumentech před uložením.

    Výchozí pravidla pokrývají e-maily, IČO-like vzory, telefonní čísla
    a rodná čísla. Pravidla lze rozšířit přes configs/pipeline.yaml.
    """

    DEFAULT_RULES: list[dict[str, str]] = [
        {
            "name": "email",
            "pattern": r"\b[\w.-]+@[\w.-]+\.\w+\b",
            "replacement": "[REDACTED_EMAIL]",
        },
        {
            "name": "ico_like",
            "pattern": r"\b[A-ZŽŘŠČČŇ]{2,}[0-9]{3,}\b",
            "replacement": "[REDACTED_ID]",
        },
        {
            "name": "phone",
            "pattern": r"\b\+?[0-9][0-9\s\-]{7,}[0-9]\b",
            "replacement": "[REDACTED_PHONE]",
        },
        {
            "name": "rc_like",
            "pattern": r"\b[0-9]{6}\/?[0-9]{3,4}\b",
            "replacement": "[REDACTED_RC]",
        },
    ]

    def __init__(self, rules: list[dict[str, str]] | None = None) -> None:
        self.rules = rules or self.DEFAULT_RULES
        self._compiled = [(r["name"], re.compile(r["pattern"]), r["replacement"]) for r in self.rules]

    def anonymize(self, document: dict[str, Any]) -> dict[str, Any]:
        """Rekurzivně anonymizuje všechny řetězcové hodnoty ve slovníku."""
        return self._anonymize_value(document)

    def _anonymize_value(self, value: Any) -> Any:
        if isinstance(value, str):
            for _name, compiled, replacement in self._compiled:
                value = compiled.sub(replacement, value)
            return value
        if isinstance(value, dict):
            return {k: self._anonymize_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._anonymize_value(v) for v in value]
        return value