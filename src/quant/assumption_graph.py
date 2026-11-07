"""Graf předpokladů s přepočtem dotčených větví při změně hodnoty."""
from __future__ import annotations


class AssumptionGraph:
    def recompute(self, assumption_id: str, new_value: float | str | bool) -> dict:
        return {"assumption_id": assumption_id, "affected": []}