"""Graf předpokladů s přepočtem dotčených větví při změně hodnoty."""
from __future__ import annotations

from typing import Any


class AssumptionGraph:
    """Modeluje závislosti mezi předpoklady a odvozenými výpočty."""

    def __init__(self) -> None:
        self._assumptions: dict[str, dict[str, Any]] = {}
        self._dependents: dict[str, list[str]] = {}

    def add_assumption(
        self,
        assumption_id: Any,
        value: Any,
        depends_on: Any = None,
    ) -> None:
        """Registruje předpoklad s volitelnými dépendencemi."""
        if depends_on is None:
            deps: list[Any] = []
        elif isinstance(depends_on, (list, tuple)):
            deps = list(depends_on)
        else:
            deps = [depends_on]

        self._assumptions[assumption_id] = {
            "value": value,
            "depends_on": deps,
        }
        self._dependents.setdefault(assumption_id, [])
        for dep in deps:
            self._dependents.setdefault(dep, []).append(assumption_id)

    def get(self, assumption_id: Any) -> dict[str, Any] | None:
        return self._assumptions.get(assumption_id)

    def set(self, assumption_id: Any, value: Any) -> None:
        """Nastaví hodnotu předpokladu."""
        if assumption_id not in self._assumptions:
            raise ValueError(f"Předpoklad '{assumption_id}' neexistuje.")
        self._assumptions[assumption_id]["value"] = value

    def recompute(
        self, assumption_id: Any, new_value: Any
    ) -> dict[str, Any]:
        """Změní hodnotu předpokladu a vrátí seznam ovlivněných předpokladů."""
        self.set(assumption_id, new_value)
        affected = self._collect_affected(assumption_id)
        return {
            "assumption_id": assumption_id,
            "new_value": new_value,
            "affected": affected,
        }

    def _collect_affected(self, assumption_id: Any) -> list[str]:
        """Iterativně (bez rekurze) shromáždí ovlivněné předpoklady."""
        affected: list[Any] = []
        visited: set[Any] = set()
        stack: list[Any] = list(self._dependents.get(assumption_id, []))
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            affected.append(node)
            for child in self._dependents.get(node, []):
                if child not in visited:
                    stack.append(child)
        return affected

    def list_assumptions(self) -> list[Any]:
        return sorted(self._assumptions.keys())
