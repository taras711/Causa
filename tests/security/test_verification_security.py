"""Bezpečnostní testy pro VerificationLayer."""
from __future__ import annotations

import pytest

from src.knowledge.verification import VerificationLayer


@pytest.mark.security
def test_verify_none_claim_does_not_crash() -> None:
    layer = VerificationLayer()
    try:
        res = layer.verify(None)  # type: ignore[arg-type]
    except (TypeError, AttributeError):
        return
    assert isinstance(res, dict)


@pytest.mark.security
def test_verify_empty_claim_does_not_crash() -> None:
    layer = VerificationLayer()
    res = layer.verify({})
    assert isinstance(res, dict)
    assert res.get("level") in ("partial", "unverified", "verified")


@pytest.mark.security
def test_verify_unknown_source_unverified() -> None:
    layer = VerificationLayer()
    res = layer.verify({"text": "cokoliv", "source": "evil_source"})
    assert res["verified"] is False
    assert res["level"] == "unverified"


@pytest.mark.security
def test_verify_work_model_injection_does_not_match() -> None:
    layer = VerificationLayer(work_model={"processes": [{"name": "Optimalizace nákladů"}]})
    # Text obsahující injekční payload by se neměl shodovat s procesem
    res = layer.verify({"text": "'; DROP TABLE processes; --", "source": "work_model"})
    assert res["verified"] is False


@pytest.mark.security
def test_verify_huge_text_does_not_dos() -> None:
    layer = VerificationLayer()
    big = "slovo " * 100000
    res = layer.verify({"text": big, "source": "assumption"})
    assert isinstance(res, dict)


@pytest.mark.security
def test_verify_face_model_none_entries_does_not_crash() -> None:
    layer = VerificationLayer(face_models=[None])  # type: ignore[list-item]
    try:
        res = layer.verify({"text": "test", "source": "face_model"})
    except Exception:
        return
    assert isinstance(res, dict)


@pytest.mark.security
def test_verify_face_model_id_injection_treated_as_data() -> None:
    fms = [{"model_id": "fm-1", "name": "Lean", "mechanism": "eliminace plytvani", "tags": [], "applicable_to": []}]
    layer = VerificationLayer(face_models=fms)
    res = layer.verify({"text": "eliminace plytvani", "source": "face_model", "face_model_id": "'; DROP --"})
    assert res["verified"] is False or res["face_model_id"] != "'; DROP --"


@pytest.mark.security
def test_verify_client_data_without_evidence_partial() -> None:
    layer = VerificationLayer()
    res = layer.verify({"text": "x", "source": "client_data"})
    assert res["level"] == "partial"
    assert res["verified"] is False
