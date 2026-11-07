"""Monte Carlo simulace pro odhad nejlepšího/horšího scénáře."""
from __future__ import annotations


class MonteCarlo:
    def simulate(self, model: dict, iterations: int = 1000) -> dict:
        return {"iterations": iterations, "results": []}