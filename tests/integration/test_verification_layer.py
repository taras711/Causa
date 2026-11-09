"""Integrační testy: VerificationLayer – ověření tvrzení proti work_model, client_data, assumption."""

from __future__ import annotations

from src.knowledge.verification import VerificationLayer


class TestVerificationLayer:
    """Verifikační vrsta musí přiřadit správnou úroveň (unverified / partial / verified)."""

    def test_assumption_claim_is_always_partial(self) -> None:
        layer = VerificationLayer()
        claim = {
            "text": "Gamifikace zvysuje motivaci.",
            "source": "assumption",
            "confidence": 0.5,
        }
        result = layer.verify(claim)
        assert result["verified"] is False
        assert result["level"] == "partial"

    def test_work_model_matching_claim_is_verified(self) -> None:
        layer = VerificationLayer(
            work_model={"processes": [{"name": "5S"}, {"name": "Kaizen"}]}
        )
        claim = {
            "text": "Metoda 5S zlepšuje pracovní prostředí.",
            "source": "work_model",
        }
        result = layer.verify(claim)
        assert result["verified"] is True
        assert result["level"] == "verified"

    def test_work_model_non_matching_claim_is_unverified(self) -> None:
        layer = VerificationLayer(
            work_model={"processes": [{"name": "5S"}]}
        )
        claim = {
            "text": "Nějaká jiná metoda, která není v modelu.",
            "source": "work_model",
        }
        result = layer.verify(claim)
        assert result["verified"] is False
        assert result["level"] == "unverified"

    def test_client_data_with_evidence_is_verified(self) -> None:
        layer = VerificationLayer()
        claim = {
            "text": "70 % uzivatelu nepozivaji dashboard.",
            "source": "client_data",
            "evidence": "Anonymizovana data usage analytics.",
        }
        result = layer.verify(claim)
        assert result["verified"] is True
        assert result["level"] == "verified"

    def test_client_data_without_evidence_is_partial(self) -> None:
        layer = VerificationLayer()
        claim = {
            "text": "70 % uzivatelu nepozivaji dashboard.",
            "source": "client_data",
        }
        result = layer.verify(claim)
        assert result["verified"] is False
        assert result["level"] == "partial"

    def test_unknown_source_is_unverified(self) -> None:
        layer = VerificationLayer()
        claim = {
            "text": "Nějaké tvrzení.",
            "source": "unknown_source",
        }
        result = layer.verify(claim)
        assert result["verified"] is False
        assert result["level"] == "unverified"

    def test_empty_work_model_means_no_work_model_claim_can_match(self) -> None:
        layer = VerificationLayer()
        claim = {
            "text": "5S zlepšuje pracovní prostředí.",
            "source": "work_model",
        }
        result = layer.verify(claim)
        assert result["verified"] is False
        assert result["level"] == "unverified"
