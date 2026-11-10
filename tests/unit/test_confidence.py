"""Unit testy pro src/quant/confidence.py — deterministické, kalibrovatelné confidence skóre."""

from __future__ import annotations

from src.quant.confidence import ConfidenceCalculator, ConfidenceComponents


def test_score_full_is_one() -> None:
    calc = ConfidenceCalculator()
    comps = ConfidenceComponents(1.0, 1.0, 1.0, 1.0, 1.0)
    assert calc.score(comps)["confidence"] == 1.0


def test_score_empty_is_zero() -> None:
    calc = ConfidenceCalculator()
    comps = ConfidenceComponents(0.0, 0.0, 0.0, 0.0, 0.0)
    assert calc.score(comps)["confidence"] == 0.0


def test_score_is_clamped_to_zero_one() -> None:
    calc = ConfidenceCalculator()
    comps = ConfidenceComponents(2.0, -1.0, 3.0, 0.5, 0.0)
    assert 0.0 <= calc.score(comps)["confidence"] <= 1.0


def test_weights_sum_to_one() -> None:
    calc = ConfidenceCalculator()
    assert abs(sum(calc.weights.values()) - 1.0) < 1e-9


def test_bands() -> None:
    calc = ConfidenceCalculator()
    assert calc.score(ConfidenceComponents(0.2, 0.2, 0.2, 0.2, 0.2))["band"] == "low"
    assert calc.score(ConfidenceComponents(0.55, 0.55, 0.55, 0.55, 0.55))["band"] == "medium"
    assert calc.score(ConfidenceComponents(0.9, 0.9, 0.9, 0.9, 0.9))["band"] == "high"


def test_from_claims_empty() -> None:
    comps = ConfidenceCalculator.from_claims([])
    assert comps.source_quality == 0.0
    assert comps.source_count == 0.0


def test_from_claims_sources_and_levels() -> None:
    claims = [
        {"id": 1, "source": "client_data", "evidence": "data export"},
        {"id": 2, "source": "assumption", "assumption": True},
        {"id": 3, "source": "work_model"},
    ]
    comps = ConfidenceCalculator.from_claims(
        claims,
        levels=["verified", "unverified", "partial"],
        agreement=0.6,
        independent_sources=3,
    )
    assert comps.source_count == 1.0  # 3 independent sources / 3
    assert comps.verification == (1.0 + 0.0 + 0.5) / 3
    assert comps.agreement == 0.6
    assert 0.3 < comps.source_quality < 0.9


def test_from_claims_data_completeness() -> None:
    claims = [
        {"id": 1, "source": "client_data", "evidence": "x"},
        {"id": 2, "source": "client_data"},
    ]
    comps = ConfidenceCalculator.from_claims(claims)
    assert comps.data_completeness == 0.5

    comps2 = ConfidenceCalculator.from_claims([{"id": 1, "source": "work_model"}])
    assert comps2.data_completeness == 1.0  # žádná client data = neutrální


def test_custom_weights_normalized() -> None:
    calc = ConfidenceCalculator(weights={"source_quality": 1.0, "source_count": 1.0})
    assert abs(sum(calc.weights.values()) - 1.0) < 1e-9
    assert calc.weights["source_quality"] == 0.5
    assert calc.weights["source_count"] == 0.5