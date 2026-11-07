"""Verifikační vrstva – ověření tvrzení proti WorkModelu, datům klienta nebo předpokladům."""
from __future__ import annotations

from typing import Any


class VerificationLayer:
    """Ověřuje tvrzení a přiřazuje úroveň: unverified / partial / verified.

    Zdroje pravdy:
      - work_model – schválené pracovní modely firmy
      - client_data – data klienta
      - assumption – explicitně označený předpoklad (vždy jen 'partial')
    """

    def __init__(self, work_model: dict[str, Any] | None = None) -> None:
        self.work_model = work_model or {}

    def verify(self, claim: dict[str, Any]) -> dict[str, Any]:
        """Vrátí verifikační výsledek pro dané tvrzení.

        Očekávané klíče v claim:
          - text: text tvrzení
          - source: work_model | client_data | assumption
          - evidence: volitelné odkazy na důkazy
        """
        text = claim.get("text", "")
        source = claim.get("source", "assumption")
        evidence = claim.get("evidence")

        if source == "assumption":
            return {
                "verified": False,
                "level": "partial",
                "notes": "Tvrzení je založeno na předpokladu, ne na ověřených datech.",
            }

        if source == "work_model":
            if self._matches_work_model(text):
                return {
                    "verified": True,
                    "level": "verified",
                    "notes": "Tvrzení odpovídá schválenému WorkModelu.",
                }
            return {
                "verified": False,
                "level": "unverified",
                "notes": "Tvrzení se neshoduje s WorkModelem.",
            }

        if source == "client_data":
            if evidence:
                return {
                    "verified": True,
                    "level": "verified",
                    "notes": "Tvrzení je podloženo daty klienta.",
                }
            return {
                "verified": False,
                "level": "partial",
                "notes": "Zdroj je client_data, ale chybí konkrétní důkaz.",
            }

        return {
            "verified": False,
            "level": "unverified",
            "notes": "Neznámý zdroj tvrzení.",
        }

    def _matches_work_model(self, text: str) -> bool:
        """Jednoduchá kontrola shody s WorkModelem (keyword-based)."""
        if not self.work_model:
            return False
        text_lower = text.lower()
        processes = self.work_model.get("processes", [])
        for proc in processes:
            proc_name = str(proc.get("name", "")).lower()
            if proc_name and proc_name in text_lower:
                return True
        return False