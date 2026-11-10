"""Kalibrovatelné confidence skóre pro výstupy analýzy.

Pravidlo: sebereflexe LLM (např. "confidence: 0.85") není kalibrovaná
pravděpodobnost správnosti. Vystavíme deterministickým výpočtem složené
skóre z vlastností důkazů:

  * kvalita zdroje        work_model > client_data > face_model > assumption > unknown
  * počet nezávislých zdrojů
  * shoda napříč během / modely (agreement)
  * výsledek verifikace   verified / partial / unverified
  * úplnost dat klienta   (důkaz k client_data claimům)

Výstup je v intervalu [0, 1] s pásmem (low/medium/high) a rozkladem
jednotlivých složek. Položka calibrated je připravena pro dodatečnou
kalibraci proti reálným výsledkům z praxe (učící smyčka), zatím je
vypnutá (calibrated = False).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_SOURCE_QUALITY: dict[str, float] = {
    "work_model": 0.95,
    "client_data": 0.85,
    "face_model": 0.80,
    "assumption": 0.35,
    "unknown": 0.10,
}

_LEVEL_VALUE: dict[str, float] = {
    "verified": 1.0,
    "partial": 0.50,
    "unverified": 0.0,
}

_BAND_LOW = 0.40
_BAND_HIGH = 0.70

_DEFAULT_WEIGHTS: dict[str, float] = {
    "source_quality": 0.30,
    "source_count": 0.20,
    "agreement": 0.25,
    "verification": 0.15,
    "data_completeness": 0.10,
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class ConfidenceComponents:
    """Vstupní složky pro výpočet confidence. Všechny v intervalu [0, 1]."""

    source_quality: float
    source_count: float
    agreement: float
    verification: float
    data_completeness: float


class ConfidenceCalculator:
    """Deterministický výpočet složeného confidence skóre."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = dict(_DEFAULT_WEIGHTS)
        if weights:
            total = sum(float(v) for v in weights.values())
            if total > 0:
                self.weights = {k: float(v) / total for k, v in weights.items()}

    def score(self, components: ConfidenceComponents) -> dict[str, Any]:
        """Vrátí confidence [0, 1], pásmo a rozklad složek."""
        values = {
            "source_quality": components.source_quality,
            "source_count": components.source_count,
            "agreement": components.agreement,
            "verification": components.verification,
            "data_completeness": components.data_completeness,
        }
        weighted = sum(self.weights[k] * values[k] for k in self.weights)
        raw = _clamp(round(weighted, 4))

        if raw < _BAND_LOW:
            band = "low"
        elif raw < _BAND_HIGH:
            band = "medium"
        else:
            band = "high"

        return {
            "confidence": raw,
            "confidence_percent": round(raw * 100, 1),
            "band": band,
            "components": dict(values),
            "weights": dict(self.weights),
            # True až po kalibraci nad reálnými výsledky z pilotu / ledgeru.
            "calibrated": False,
        }

    @classmethod
    def from_claims(
        cls,
        claims: list[dict[str, Any]],
        levels: list[str] | None = None,
        agreement: float = 0.0,
        independent_sources: int | None = None,
    ) -> ConfidenceComponents:
        """Sestaví složky ze claimů Case a volitelných verifikačních úrovní."""
        if not claims:
            return ConfidenceComponents(
                source_quality=0.0,
                source_count=0.0,
                agreement=_clamp(agreement),
                verification=0.0,
                data_completeness=0.0,
            )

        qualities = [
            _SOURCE_QUALITY.get(str(c.get("source", "unknown")), 0.10) for c in claims
        ]
        source_quality = sum(qualities) / len(qualities)

        sources = {str(c.get("source", "unknown")) for c in claims}
        count = independent_sources if independent_sources is not None else len(sources)
        source_count = _clamp(count / 3.0)

        if levels:
            values = [_LEVEL_VALUE.get(str(l), 0.0) for l in levels]
            verification = sum(values) / len(values)
        else:
            verified_claims = sum(1 for c in claims if c.get("verified") is True)
            verification = verified_claims / len(claims)

        client_claims = [c for c in claims if c.get("source") == "client_data"]
        if client_claims:
            with_evidence = sum(1 for c in client_claims if c.get("evidence"))
            data_completeness = with_evidence / len(client_claims)
        else:
            data_completeness = 1.0

        return ConfidenceComponents(
            source_quality=round(source_quality, 4),
            source_count=round(source_count, 4),
            agreement=_clamp(agreement),
            verification=round(verification, 4),
            data_completeness=round(data_completeness, 4),
        )