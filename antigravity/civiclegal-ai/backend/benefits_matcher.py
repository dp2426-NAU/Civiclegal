"""
CivicLegal AI — Benefits Matcher
Matches users to federal/state benefit programs based on eligibility criteria.
DEMO DATA – NOT LEGAL ADVICE
"""
import os
from typing import Optional


FEDERAL_POVERTY_LEVEL_2024 = {
    1: 15060, 2: 20440, 3: 25820, 4: 31200,
    5: 36580, 6: 41960, 7: 47340, 8: 52720,
}

BENEFIT_PROGRAMS = {
    "SNAP": {
        "name": "Supplemental Nutrition Assistance Program (SNAP)",
        "description": "Provides nutrition benefits to supplement the food budget of low-income families.",
        "income_threshold_pct": 1.30,
        "requires_children": False,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Photo ID", "Proof of income (pay stubs, tax returns)", "Proof of residency", "Social Security numbers for all household members"],
        "link": "https://www.fns.usda.gov/snap/eligibility",
        "agency": "USDA Food and Nutrition Service",
    },
    "Medicaid": {
        "name": "Medicaid",
        "description": "Health coverage for low-income adults, children, pregnant women, elderly, and people with disabilities.",
        "income_threshold_pct": 1.38,
        "requires_children": False,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Photo ID", "Proof of income", "Proof of citizenship or immigration status", "Social Security number"],
        "link": "https://www.medicaid.gov/medicaid/eligibility/index.html",
        "agency": "Centers for Medicare & Medicaid Services",
    },
    "CHIP": {
        "name": "Children's Health Insurance Program (CHIP)",
        "description": "Low-cost health coverage for children in families that earn too much to qualify for Medicaid.",
        "income_threshold_pct": 2.00,
        "requires_children": True,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Proof of child's age (birth certificate)", "Proof of income", "Proof of residency", "Social Security number"],
        "link": "https://www.insurekidsnow.gov/coverage/index.html",
        "agency": "Centers for Medicare & Medicaid Services",
    },
    "WIC": {
        "name": "Women, Infants, and Children (WIC)",
        "description": "Nutrition program for pregnant women, new mothers, and children under age 5.",
        "income_threshold_pct": 1.85,
        "requires_children": False,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": 5,
        "documents": ["Proof of identity", "Proof of income", "Proof of residency", "Documentation of pregnancy or child's age"],
        "link": "https://www.fns.usda.gov/wic/eligibility",
        "agency": "USDA Food and Nutrition Service",
    },
    "TANF": {
        "name": "Temporary Assistance for Needy Families (TANF)",
        "description": "Cash assistance and work support for low-income families with children.",
        "income_threshold_pct": 0.50,
        "requires_children": True,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Birth certificates for children", "Proof of income", "Proof of residency", "Social Security numbers"],
        "link": "https://www.acf.hhs.gov/ofa/programs/tanf",
        "agency": "HHS Office of Family Assistance",
    },
    "Section 8": {
        "name": "Section 8 Housing Choice Voucher",
        "description": "Rental assistance allowing low-income families to choose housing in the private market.",
        "income_threshold_pct": 0.50,
        "requires_children": False,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Photo ID", "Social Security card", "Proof of income", "Birth certificates", "Current lease or eviction notice"],
        "link": "https://www.hud.gov/program_offices/public_indian_housing/programs/hcv",
        "agency": "HUD Office of Public and Indian Housing",
    },
    "SSI": {
        "name": "Supplemental Security Income (SSI)",
        "description": "Monthly payments for people with disabilities or age 65+ with limited income and resources.",
        "income_threshold_pct": 0.75,
        "requires_children": False,
        "requires_disability": True,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Social Security card", "Birth certificate or proof of age", "Medical records documenting disability", "Proof of income and resources"],
        "link": "https://www.ssa.gov/ssi/",
        "agency": "Social Security Administration",
    },
    "SSDI": {
        "name": "Social Security Disability Insurance (SSDI)",
        "description": "Benefits for people who have worked and paid Social Security taxes and have a qualifying disability.",
        "income_threshold_pct": 2.00,
        "requires_children": False,
        "requires_disability": True,
        "requires_veteran": False,
        "min_age": 18,
        "max_age": 65,
        "documents": ["Social Security card", "Work history (W-2s, tax returns)", "Medical records", "Doctor's contact information"],
        "link": "https://www.ssa.gov/disability/",
        "agency": "Social Security Administration",
    },
    "EITC": {
        "name": "Earned Income Tax Credit (EITC)",
        "description": "Tax credit for low- to moderate-income workers and families, especially those with children.",
        "income_threshold_pct": 2.00,
        "requires_children": False,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": 25,
        "max_age": None,
        "documents": ["Valid Social Security number", "Prior year tax return", "Proof of earned income", "Filing status documentation"],
        "link": "https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit",
        "agency": "IRS",
    },
    "LIHEAP": {
        "name": "Low Income Home Energy Assistance Program (LIHEAP)",
        "description": "Helps low-income households pay for home heating and cooling costs.",
        "income_threshold_pct": 1.50,
        "requires_children": False,
        "requires_disability": False,
        "requires_veteran": False,
        "min_age": None,
        "max_age": None,
        "documents": ["Proof of income", "Recent utility bills", "Proof of residency", "Social Security numbers"],
        "link": "https://www.acf.hhs.gov/ocs/programs/liheap",
        "agency": "HHS Office of Community Services",
    },
}


class BenefitsMatcher:
    def __init__(self):
        self.use_demo = os.getenv("USE_DEMO_DATA", "true").lower() == "true"

    def _get_fpl(self, household_size: int) -> float:
        size = min(max(household_size, 1), 8)
        base = FEDERAL_POVERTY_LEVEL_2024.get(size, 52720)
        if household_size > 8:
            base += (household_size - 8) * 5380
        return base

    def match(
        self,
        household_size: int,
        annual_income: float,
        state: str,
        has_children: bool = False,
        has_disability: bool = False,
        is_veteran: bool = False,
        age: Optional[int] = None,
    ) -> list:
        fpl = self._get_fpl(household_size)
        income_pct = annual_income / fpl if fpl > 0 else 999
        matched = []

        for program_key, program in BENEFIT_PROGRAMS.items():
            eligible, reason = self._check_eligibility(
                program, income_pct, has_children, has_disability, is_veteran, age
            )
            if eligible:
                matched.append({
                    "program": program["name"],
                    "program_key": program_key,
                    "description": program["description"],
                    "eligibility": True,
                    "reason": reason,
                    "documents_needed": program["documents"],
                    "link": program["link"],
                    "agency": program["agency"],
                    "demo_label": "[DEMO DATA – NOT LEGAL ADVICE]" if self.use_demo else None,
                })

        if not matched:
            matched.append({
                "program": "No Direct Match Found",
                "program_key": "none",
                "description": "Based on the information provided, you may not qualify for the programs checked. You may still be eligible for state-specific programs.",
                "eligibility": False,
                "reason": f"Annual income (${annual_income:,.0f}) exceeds thresholds for common federal programs at {income_pct:.0%} of Federal Poverty Level.",
                "documents_needed": [],
                "link": "https://www.benefits.gov",
                "agency": "Benefits.gov",
                "demo_label": "[DEMO DATA – NOT LEGAL ADVICE]" if self.use_demo else None,
            })

        return matched

    def _check_eligibility(
        self, program: dict, income_pct: float,
        has_children: bool, has_disability: bool, is_veteran: bool, age: Optional[int]
    ) -> tuple:
        if income_pct > program["income_threshold_pct"]:
            return False, f"Income exceeds {program['income_threshold_pct']*100:.0f}% of Federal Poverty Level"

        if program["requires_children"] and not has_children:
            return False, "Program requires dependent children in household"

        if program["requires_disability"] and not has_disability:
            return False, "Program requires documented disability"

        if program["requires_veteran"] and not is_veteran:
            return False, "Program requires veteran status"

        if age is not None:
            if program["min_age"] and age < program["min_age"]:
                return False, f"Minimum age requirement: {program['min_age']}"
            if program["max_age"] and age > program["max_age"]:
                return False, f"Maximum age limit: {program['max_age']}"

        reasons = [f"Income at {income_pct:.0%} of FPL meets the {program['income_threshold_pct']*100:.0f}% threshold"]
        if has_disability and program.get("requires_disability"):
            reasons.append("Disability status verified")
        if has_children and program.get("requires_children"):
            reasons.append("Dependent children in household")

        return True, "; ".join(reasons)
