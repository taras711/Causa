"""Graf předpokladů s přepočtem dotčených větví při změně hodnoty."""
from __future__ import annotations

from typing import Any


class AssumptionGraph:
    """Modeluje závislosti mezi předpoklady a odvozenými výpočty.

    Při změně hodnoty předpokladu se automaticky přepočítají všechny
    dotčené větve (např. ROI, citlivost, Monte Carlo výsledky).
    """

    def __init__(self) -> None:
        self._assumptions: dict[str, dict[str, Any]] = {}
        self._dependents: dict[str, list[str]] = {}  # assumption_id -> list of dependent ids

    def add_assumption(
        self,
        assumption_id: str,
        value: float | str | bool,
        depends_on: list[str] | None = None,
    ) -> None:
        """Registruje předpoklad s volitelnými dépendencemi."""
        self._assumptions[assumption_id] = {
            "value": value,
            "depends_on": depends_on or [],
        }
        self._dependents.setdefault(assumption_id, [])
        for dep in (depends_on or []):
            self._dependents.setdefault(dep, []).append(assumption_id)

    def get(self, assumption_id: str) -> dict[str, Any] | None:
        return self._assumptions.get(assumption_id)

    def set(self, assumption_id: str, value: float | str | bool) -> None:
        """Nastaví hodnotu předpokladu."""
        if assumption_id not in self._assumptions:
            raise ValueError(f"Předpoklad '{assumption_id}' neexistuje.")
        self._assumptions[assumption_id]["value"] = value

    def recompute(
        self, assumption_id: str, new_value: float | str | bool
    ) -> dict[str, Any]:
        """Změní hodnotu předpokladu a vrátí seznam ovlivněných předpokladů."""
        self.set(assumption_id, new_value)
        affected = self._collect_affected(assumption_id)
        return {
            "assumption_id": assumption_id,
            "new_value": new_value,
            "affected": affected,
        }

    def _collect_affected(self, assumption_id: str) -> list[str]:
        """Rekurzivně shromáždí všechny předpoklady, které závisí na daném."""
        affected: list[str] = []
        visited: set[str] = set()

        def dfs(node: str) -> None:
            for child in self._dependents.get(node, []):
                if child not in visited:
                    visited.add(child)
                    affected.append(child)
                    dfs(child)

        dfs(assumption_id)
        return affected

    def list_assumptions(self) -> list[str]:
        return sorted(self._assumptions.keys())