"""
CivicLegal AI — Benefits.gov API Client
Fetches benefit program data. Falls back to demo data if unavailable.
DEMO DATA – NOT LEGAL ADVICE
"""
import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

BENEFITS_API_BASE = "https://www.benefits.gov/api"
DEMO_BENEFITS = [
    {
        "id": "SNAP",
        "title": "Supplemental Nutrition Assistance Program",
        "agency": "USDA",
        "summary": "SNAP provides nutrition benefits to supplement the food budget of needy families.",
        "url": "https://www.benefits.gov/benefit/361",
        "source": "[DEMO DATA]",
    },
    {
        "id": "Medicaid",
        "title": "Medicaid",
        "agency": "HHS",
        "summary": "Medicaid provides health coverage to low-income individuals and families.",
        "url": "https://www.benefits.gov/benefit/1",
        "source": "[DEMO DATA]",
    },
]


class BenefitsGovClient:
    def __init__(self):
        self.use_demo = os.getenv("USE_DEMO_DATA", "true").lower() == "true"

    async def search_benefits(self, query: str, limit: int = 5) -> list:
        if self.use_demo:
            logger.info("Benefits.gov API: using demo data")
            return DEMO_BENEFITS[:limit]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{BENEFITS_API_BASE}/benefits",
                    params={"query": query, "limit": limit},
                )
                resp.raise_for_status()
                return resp.json().get("benefits", [])
        except Exception as e:
            logger.error(f"Benefits.gov API error: {e}. Using demo data.")
            return DEMO_BENEFITS[:limit]

    async def get_benefit_details(self, benefit_id: str) -> Optional[dict]:
        if self.use_demo:
            return DEMO_BENEFITS[0]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{BENEFITS_API_BASE}/benefits/{benefit_id}")
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Benefits.gov fetch error: {e}")
            return None
