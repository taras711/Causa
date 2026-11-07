"""Unit testy pro verifikační vrstvu."""

from __future__ import annotations

import pytest

from src.knowledge.verification import VerificationLayer


@pytest.fixture
def work_model() -> dict:
    return {
        "processes": [
            {"name": "Schvalování faktur"},
            {"name": "Optimalizace nákladů"},
            {"name": "Řízení dodací lhůty"},
        ]
    }


@pytest.fixture
def face_models() -> list[dict]:
    return [
        {
            "model_id": "fm-001",
            "name": "Lean Manufacturing",
            "mechanism": "Eliminace plýtvání prostřednictvím kontinuálního zlepšování",
            "applicable_to": ["výroba"],
            "tags": ["efektivita", "náklady"],
        },
        {
            "model_id": "fm-002",
            "name": "Six Sigma",
            "mechanism": "Snížení variability procesů pomocí statistických metod",
            "applicable_to": ["kvalita", "výroba"],
            "tags": ["kvalita", "statistika"],
        },
    ]


# ------------------------------------------------------------------ #
# Základní verifikace (zdroje: assumption, work_model, client_data)
# ------------------------------------------------------------------ #

def test_verify_assumption_returns_partial() -> None:
    layer = VerificationLayer()
    result = layer.verify(
        {
            "text": "Náklady klesnou o 20 %",
            "source": "assumption",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "partial"
    assert "předpokladu" in result["notes"]


def test_verify_work_model_match(work_model: dict) -> None:
    layer = VerificationLayer(work_model=work_model)
    result = layer.verify(
        {
            "text": "Proces schvalování faktur je klíčový",
            "source": "work_model",
        }
    )
    assert result["verified"] is True
    assert result["level"] == "verified"
    assert result["source"] == "work_model"


def test_verify_work_model_no_match(work_model: dict) -> None:
    layer = VerificationLayer(work_model=work_model)
    result = layer.verify(
        {
            "text": "Něco úplně jiného co v modelu není",
            "source": "work_model",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "unverified"


def test_verify_client_data_with_evidence() -> None:
    layer = VerificationLayer()
    result = layer.verify(
        {
            "text": "Výnosy klesly o 10 %",
            "source": "client_data",
            "evidence": "Finanční výkaz 2024",
        }
    )
    assert result["verified"] is True
    assert result["level"] == "verified"
    assert result["source"] == "client_data"


def test_verify_client_data_without_evidence() -> None:
    layer = VerificationLayer()
    result = layer.verify(
        {
            "text": "Výnosy klesly o 10 %",
            "source": "client_data",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "partial"


def test_verify_unknown_source() -> None:
    layer = VerificationLayer()
    result = layer.verify(
        {
            "text": "Nějaké tvrzení",
            "source": "neznamy_zdroj",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "unverified"


# ------------------------------------------------------------------ #
# Verifikace proti FaceModel vzorům
# ------------------------------------------------------------------ #

def test_verify_against_face_model_match(face_models: list[dict]) -> None:
    layer = VerificationLayer(face_models=face_models)
    result = layer.verify(
        {
            "text": "Eliminace plýtvání a kontinuální zlepšování procesů",
            "source": "face_model",
        }
    )
    assert result["verified"] is True
    assert result["level"] == "verified"
    assert result["source"] == "face_model"
    assert result["face_model_id"] == "fm-001"


def test_verify_against_face_model_no_match(face_models: list[dict]) -> None:
    layer = VerificationLayer(face_models=face_models)
    result = layer.verify(
        {
            "text": "Něco co vůbec neodpovídá žádnému vzoru",
            "source": "face_model",
        }
    )
    assert result["verified"] is False
    assert result["level"] in ("unverified", "partial")


def test_verify_against_face_model_empty_list() -> None:
    layer = VerificationLayer(face_models=[])
    result = layer.verify(
        {
            "text": "Nějaké tvrzení",
            "source": "face_model",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "unverified"
    assert result["face_model_id"] is None


def test_verify_against_face_model_specific_id(face_models: list[dict]) -> None:
    layer = VerificationLayer(face_models=face_models)
    result = layer.verify(
        {
            "text": "Snížení variability procesů",
            "source": "face_model",
            "face_model_id": "fm-002",
        }
    )
    assert result["face_model_id"] == "fm-002"
    assert result["verified"] is True


def test_verify_against_face_model_nonexistent_id(face_models: list[dict]) -> None:
    layer = VerificationLayer(face_models=face_models)
    result = layer.verify(
        {
            "text": "Nějaké tvrzení",
            "source": "face_model",
            "face_model_id": "neexistuje",
        }
    )
    assert result["verified"] is False
    assert result["level"] == "unverified"


def test_verify_against_face_model_partial_match(face_models: list[dict]) -> None:
    layer = VerificationLayer(face_models=face_models)
    # Tvrzení s velmi nízkou shodou → partial
    result = layer.verify(
        {
            "text": "Abcdefgh ijklmnop",
            "source": "face_model",
        }
    )
    assert result["level"] in ("unverified", "partial")