"""Bezpečnostní testy anonymizace citlivých dat před uložením do knowledge base."""

from __future__ import annotations

import pytest

from src.knowledge.anonymization import Anonymizer
from src.knowledge.ingestion import IngestionPipeline


class TestAnonymizerDefaultRules:
    """Výchozí pravidla anonymizace (e-mail, IČO-like, telefon, rodné číslo)."""

    def test_redacts_email(self) -> None:
        anonymizer = Anonymizer()
        doc = {"text": "Kontakt: jan.novak@firma.cz, prosím odpovězte."}
        result = anonymizer.anonymize(doc)
        assert "jan.novak@firma.cz" not in str(result)
        assert "[REDACTED_EMAIL]" in str(result)

    def test_redacts_ico_like(self) -> None:
        anonymizer = Anonymizer()
        doc = {"text": "Identifikátor společnosti: ABC123456."}
        result = anonymizer.anonymize(doc)
        assert "ABC123456" not in str(result)
        assert "[REDACTED_ID]" in str(result)

    def test_redacts_phone(self) -> None:
        anonymizer = Anonymizer()
        doc = {"text": "Telefon: +420 123 456 789."}
        result = anonymizer.anonymize(doc)
        assert "+420 123 456 789" not in str(result)
        assert "[REDACTED_PHONE]" in str(result)

    def test_redacts_rc_like(self) -> None:
        anonymizer = Anonymizer()
        doc = {"text": "Rodné číslo: 900101/1234."}
        result = anonymizer.anonymize(doc)
        assert "900101/1234" not in str(result)
        assert "[REDACTED_RC]" in str(result)

    def test_redacts_all_patterns_in_one_document(self) -> None:
        anonymizer = Anonymizer()
        doc = {
            "text": "Kontakt: jan@firma.cz, IČO: XYZ789012, tel: +420 111 222 333, RC: 850202/4567."
        }
        result = anonymizer.anonymize(doc)
        text = str(result)
        assert "jan@firma.cz" not in text
        assert "XYZ789012" not in text
        assert "+420 111 222 333" not in text
        assert "850202/4567" not in text
        assert text.count("[REDACTED_") >= 4

    def test_anonymizes_recursive_dict(self) -> None:
        anonymizer = Anonymizer()
        doc = {
            "user": {"email": "user@example.com", "phone": "+420 999 888 777"},
            "meta": [{"ico": "ABC123456"}, {"rc": "900101/1234"}],
        }
        result = anonymizer.anonymize(doc)
        assert "user@example.com" not in str(result)
        assert "+420 999 888 777" not in str(result)
        assert "ABC123456" not in str(result)
        assert "900101/1234" not in str(result)

    def test_preserves_non_string_values(self) -> None:
        anonymizer = Anonymizer()
        doc = {"count": 42, "active": True, "ratio": 3.14, "tags": ["a", "b"]}
        result = anonymizer.anonymize(doc)
        assert result["count"] == 42
        assert result["active"] is True
        assert result["ratio"] == 3.14
        assert result["tags"] == ["a", "b"]

    def test_custom_rules_are_applied(self) -> None:
        custom_rules = [
            {
                "name": "internal_code",
                "pattern": r"\bINT-[0-9]{4}\b",
                "replacement": "[REDACTED_CODE]",
            }
        ]
        anonymizer = Anonymizer(rules=custom_rules)
        doc = {"text": "Interní kód: INT-5678 a další: INT-0001."}
        result = anonymizer.anonymize(doc)
        text = str(result)
        assert "INT-5678" not in text
        assert "INT-0001" not in text
        assert text.count("[REDACTED_CODE]") == 2


class TestIngestionAnonymizesBeforeStorage:
    """Ingestní pipeline musí anonymizovat před uložením do knowledge base."""

    @pytest.mark.asyncio
    async def test_ingest_anonymizes_document(self) -> None:
        pipeline = IngestionPipeline()
        document = {
            "title": "Zpráva o incidentu",
            "content": "Kontaktujte admina na admin@firma.cz nebo +420 123 456 789.",
        }
        result = await pipeline.ingest(document)
        assert result["status"] == "ingested"
        assert result["anonymized"] is True
        doc = result["doc"]
        assert "admin@firma.cz" not in str(doc)
        assert "+420 123 456 789" not in str(doc)

    @pytest.mark.asyncio
    async def test_ingest_batch_anonymizes_all(self) -> None:
        pipeline = IngestionPipeline()
        documents = [
            {"title": "Doc 1", "content": "E-mail: a@b.cz"},
            {"title": "Doc 2", "content": "Telefon: +420 111 222 333"},
        ]
        result = await pipeline.ingest_batch(documents)
        assert result["status"] == "batch_ingested"
        assert result["count"] == 2
        for item in result["results"]:
            doc_text = str(item["doc"])
            assert "a@b.cz" not in doc_text
            assert "+420 111 222 333" not in doc_text
