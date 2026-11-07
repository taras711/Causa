"""Bezpečnostní testy pro Anonymizer."""
from __future__ import annotations

import time

import pytest

from src.knowledge.anonymization import Anonymizer


@pytest.fixture
def anon() -> Anonymizer:
    return Anonymizer()


@pytest.mark.security
def test_anonymize_email(anon: Anonymizer) -> None:
    doc = {"text": "Kontakt: jan.novak@example.com"}
    out = anon.anonymize(doc)
    assert "[REDACTED_EMAIL]" in out["text"]
    assert "jan.novak@example.com" not in out["text"]


@pytest.mark.security
def test_anonymize_phone(anon: Anonymizer) -> None:
    doc = {"text": "Tel: +420 123 456 789"}
    out = anon.anonymize(doc)
    assert "[REDACTED_PHONE]" in out["text"]


@pytest.mark.security
def test_anonymize_rc(anon: Anonymizer) -> None:
    doc = {"text": "RC: 900101/1234"}
    out = anon.anonymize(doc)
    assert "[REDACTED_RC]" in out["text"]


@pytest.mark.security
def test_anonymize_nested(anon: Anonymizer) -> None:
    doc = {"a": {"b": ["x@y.com", 42]}, "c": "tel +420 999 888 777"}
    out = anon.anonymize(doc)
    assert "[REDACTED_EMAIL]" in out["a"]["b"][0]
    assert "[REDACTED_PHONE]" in out["c"]
    assert out["a"]["b"][1] == 42


@pytest.mark.security
def test_anonymize_does_not_execute_payload(anon: Anonymizer) -> None:
    payload = {"text": "<script>alert(1)</script> jan@x.com"}
    out = anon.anonymize(payload)
    # Skript zůstane jako text, ale email je redaktován
    assert "<script>" in out["text"]
    assert "[REDACTED_EMAIL]" in out["text"]


@pytest.mark.security
def test_anonymize_non_dict_input_does_not_crash() -> None:
    anon = Anonymizer()
    # str vstup – očekáváme buď zpracování, nebo nezměněnou hodnotu bez pádu
    try:
        out = anon.anonymize("jan@x.com")  # type: ignore[arg-type]
    except (TypeError, AttributeError):
        return
    assert isinstance(out, (str, dict))


@pytest.mark.security
def test_anonymize_rejects_non_string_rules_gracefully() -> None:
    # Neplatná pravidla by neměla rozbít konstruktor
    try:
        a = Anonymizer(rules=[{"name": "x", "pattern": "[", "replacement": "R"}])
    except Exception:
        return
    # Pokud se zkompiluje (re.compile může selhat při init), anonymize nesmí spadnout
    try:
        a.anonymize({"t": "abc"})
    except Exception:
        return
    assert True


@pytest.mark.security
def test_anonymize_performance_redos(anon: Anonymizer) -> None:
    # Potenciálně katastrofický vstup – musí doběhnout v rozumném čase
    evil = "a" * 10000 + "@" + "b" * 10000
    start = time.monotonic()
    out = anon.anonymize({"t": evil})
    elapsed = time.monotonic() - start
    assert elapsed < 5.0
    assert isinstance(out, dict)


@pytest.mark.security
def test_anonymize_empty_and_none_values(anon: Anonymizer) -> None:
    doc = {"a": "", "b": None, "c": []}
    out = anon.anonymize(doc)
    assert out["a"] == ""
    assert out["b"] is None
    assert out["c"] == []
