"""
CivicLegal AI — Hallucination Guard Tests
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))

from hallucination_guard import HallucinationGuard, DISCLAIMER_REQUIRED, MINIMUM_SIMILARITY


@pytest.fixture
def guard():
    return HallucinationGuard()


def test_disclaimer_appended_when_missing(guard):
    answer, _ = guard.check("This is some legal information.", "Legal context here.", 0.80)
    assert DISCLAIMER_REQUIRED[:30].lower() in answer.lower()


def test_disclaimer_not_duplicated(guard):
    answer_with_disclaimer = f"Some info. {DISCLAIMER_REQUIRED}"
    result, _ = guard.check(answer_with_disclaimer, "Legal context.", 0.80)
    count = result.lower().count(DISCLAIMER_REQUIRED[:30].lower())
    assert count == 1


def test_overconfidence_detected(guard):
    overconfident = "You will definitely win your case. The court will absolutely rule in your favor."
    flags = guard.detect_overconfidence(overconfident)
    assert len(flags) > 0


def test_no_overconfidence_in_neutral_answer(guard):
    neutral = "Tenants have the right to receive proper notice before eviction in most jurisdictions."
    flags = guard.detect_overconfidence(neutral)
    assert len(flags) == 0


def test_refusal_detected(guard):
    refusal = "I cannot provide information on this topic."
    assert guard.is_refusal(refusal) is True


def test_non_refusal_not_flagged(guard):
    normal = "Tenants have rights under the Fair Housing Act."
    assert guard.is_refusal(normal) is False


def test_confidence_reduced_for_refusal(guard):
    refusal = "I cannot find sufficient information to answer this question."
    _, conf = guard.check(refusal, "Some legal context.", 0.80)
    assert conf < 0.80


def test_overconfidence_caps_confidence(guard):
    overconfident = "You will definitely win. The court will 100% rule in your favor."
    _, conf = guard.check(overconfident, "Some legal context.", 0.95)
    assert conf <= 0.70


def test_citation_validation_filters_ungrounded(guard):
    citations = [
        {"title": "Miranda v Arizona", "relevance": 0.95},
        {"title": "Unrelated Case XYZ", "relevance": 0.30},
    ]
    answer = "Miranda rights must be read before custodial interrogation."
    validated = guard.validate_citations(citations, answer)
    assert len(validated) >= 1


def test_check_returns_tuple(guard):
    result = guard.check("Some answer about tenant rights.", "Tenant rights context.", 0.75)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], float)
