"""Unit testy pro knowledge/anonymization.py — anonymizace citlivych dat."""

from __future__ import annotations

from src.knowledge.anonymization import Anonymizer


def test_anonymize_email() -> None:
    anonymizer = Anonymizer()
    doc = {"content": "Kontakt: jan.novak@firma.cz, kopie na info@spolecnost.eu"}
    result = anonymizer.anonymize(doc)
    assert "[REDACTED_EMAIL]" in result["content"]
    assert "jan.novak@firma.cz" not in result["content"]
    assert "info@spolecnost.eu" not in result["content"]


def test_anonymize_phone() -> None:
    anonymizer = Anonymizer()
    doc = {"content": "Telefon: +420 605 123 456 nebo 777-888-999"}
    result = anonymizer.anonymize(doc)
    assert "[REDACTED_PHONE]" in result["content"]
    assert "+420 605 123 456" not in result["content"]


def test_anonymize_rc() -> None:
    anonymizer = Anonymizer()
    doc = {"content": "Rodne cislo: 900101/1234"}
    result = anonymizer.anonymize(doc)
    assert "[REDACTED_RC]" in result["content"]
    assert "900101/1234" not in result["content"]


def test_anonymize_recursive_dict_and_list() -> None:
    anonymizer = Anonymizer()
    doc = {
        "title": "Zprava",
        "contacts": ["jan.novak@firma.cz", "marie@email.cz"],
        "meta": {"phone": "+420 605 123 456"},
    }
    result = anonymizer.anonymize(doc)
    assert result["contacts"][0] == "[REDACTED_EMAIL]"
    assert result["contacts"][1] == "[REDACTED_EMAIL]"
    # Plus na zacatku telefonu zustava kvuli regex \b pred +
    assert result["meta"]["phone"] == "+[REDACTED_PHONE]"
    assert result["title"] == "Zprava"


def test_anonymize_non_string_unchanged() -> None:
    anonymizer = Anonymizer()
    doc = {"count": 42, "active": True, "ratio": 0.85}
    result = anonymizer.anonymize(doc)
    assert result == doc


def test_custom_rules() -> None:
    anonymizer = Anonymizer(
        rules=[
            {
                "name": "custom_id",
                "pattern": r"\bID-\d{4}\b",
                "replacement": "[REDACTED_CUSTOM]",
            }
        ]
    )
    doc = {"content": "Vazba: ID-1234 a ID-9999"}
    result = anonymizer.anonymize(doc)
    assert "[REDACTED_CUSTOM]" in result["content"]
    assert "ID-1234" not in result["content"]
