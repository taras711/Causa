"""Unit testy pro knowledge/verification.py — verifikacni vrstva."""

from __future__ import annotations

from src.knowledge.verification import VerificationLayer


def test_verify_assumption_partial() -> None:
    verifier = VerificationLayer()
    result = verifier.verify(
        {
            "text": "Predpokladame rust trhu o 5 %",
            "source": "assumption",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "partial"


def test_verify_work_model_match() -> None:
    verifier = VerificationLayer(
        work_model={"processes": [{"name": "Schvaleni rozpoctu"}, {"name": "Nakup"}]}
    )
    result = verifier.verify(
        {
            "text": "Proces Schvaleni rozpoctu trva 14 dni",
            "source": "work_model",
        }
    )
    assert result["verified"] is True
    assert result["level"] == "verified"


def test_verify_work_model_no_match() -> None:
    verifier = VerificationLayer(work_model={"processes": [{"name": "Jiny proces"}]})
    result = verifier.verify(
        {
            "text": "Neznamy proces XYZ",
            "source": "work_model",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "unverified"


def test_verify_client_data_with_evidence() -> None:
    verifier = VerificationLayer()
    result = verifier.verify(
        {
            "text": "Churn je 15 %",
            "source": "client_data",
            "evidence": "analytics_export_2026.csv",
        }
    )
    assert result["verified"] is True
    assert result["level"] == "verified"


def test_verify_client_data_without_evidence_is_partial() -> None:
    verifier = VerificationLayer()
    result = verifier.verify(
        {
            "text": "Churn je 15 %",
            "source": "client_data",
        }
    )
    # client_data bez konkretniho dukazu je 'partial', ne 'unverified'
    assert result["verified"] is False
    assert result["level"] == "partial"
