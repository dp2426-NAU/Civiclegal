"""
CivicLegal AI — Benefits Matcher Tests
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from benefits_matcher import BenefitsMatcher, FEDERAL_POVERTY_LEVEL_2024


@pytest.fixture
def matcher():
    return BenefitsMatcher()


def test_fpl_household_1(matcher):
    fpl = matcher._get_fpl(1)
    assert fpl == FEDERAL_POVERTY_LEVEL_2024[1]


def test_fpl_household_4(matcher):
    fpl = matcher._get_fpl(4)
    assert fpl == FEDERAL_POVERTY_LEVEL_2024[4]


def test_fpl_large_household(matcher):
    fpl = matcher._get_fpl(10)
    base = FEDERAL_POVERTY_LEVEL_2024[8]
    assert fpl == base + 2 * 5380


def test_snap_eligible_low_income(matcher):
    results = matcher.match(household_size=2, annual_income=18000, state="CA")
    program_names = [r["program_key"] for r in results]
    assert "SNAP" in program_names


def test_snap_ineligible_high_income(matcher):
    results = matcher.match(household_size=1, annual_income=60000, state="TX")
    program_names = [r["program_key"] for r in results]
    assert "SNAP" not in program_names


def test_chip_requires_children(matcher):
    results_no_children = matcher.match(household_size=2, annual_income=25000, state="NY", has_children=False)
    results_with_children = matcher.match(household_size=3, annual_income=25000, state="NY", has_children=True)
    no_child_keys = [r["program_key"] for r in results_no_children]
    child_keys = [r["program_key"] for r in results_with_children]
    assert "CHIP" not in no_child_keys
    assert "CHIP" in child_keys


def test_ssi_requires_disability(matcher):
    results_no_disability = matcher.match(household_size=1, annual_income=8000, state="FL", has_disability=False)
    results_with_disability = matcher.match(household_size=1, annual_income=8000, state="FL", has_disability=True)
    no_dis_keys = [r["program_key"] for r in results_no_disability]
    dis_keys = [r["program_key"] for r in results_with_disability]
    assert "SSI" not in no_dis_keys
    assert "SSI" in dis_keys


def test_returns_list(matcher):
    results = matcher.match(household_size=3, annual_income=30000, state="WA")
    assert isinstance(results, list)
    assert len(results) > 0


def test_all_results_have_required_fields(matcher):
    results = matcher.match(household_size=2, annual_income=20000, state="IL", has_children=True)
    for r in results:
        assert "program" in r
        assert "eligibility" in r
        assert "reason" in r
        assert "documents_needed" in r
        assert "link" in r


def test_no_match_returns_fallback(matcher):
    results = matcher.match(household_size=1, annual_income=200000, state="CA")
    assert len(results) > 0
    assert results[0]["eligibility"] is False
