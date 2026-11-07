"""Minimální Quant Engine – deterministické výpočty (nikoli LLM-generated čísla)."""
from __future__ import annotations


class QuantEngine:
    def compute_roi(self, inputs: dict) -> dict:
        return {"roi": None, "status": "not_implemented"}

    def sensitivity(self, inputs: dict) -> dict:
        return {"results": [], "status": "not_implemented"}