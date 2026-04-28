"""
CivicLegal AI — Congress.gov API Client
Fetches legislative data. Falls back to demo data if API key unavailable.
DEMO DATA – NOT LEGAL ADVICE
"""
import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

CONGRESS_API_BASE = "https://api.congress.gov/v3"
DEMO_BILLS = [
    {
        "number": "H.R.1234",
        "title": "Tenant Protection and Housing Stability Act",
        "congress": 118,
        "type": "HR",
        "latestAction": {"text": "Referred to the Committee on Financial Services", "actionDate": "2024-01-15"},
        "url": "https://www.congress.gov/bill/118th-congress/house-bill/1234",
        "source": "[DEMO DATA]",
    },
    {
        "number": "S.567",
        "title": "Disability Rights and Accommodation Improvement Act",
        "congress": 118,
        "type": "S",
        "latestAction": {"text": "Passed Senate", "actionDate": "2024-03-22"},
        "url": "https://www.congress.gov/bill/118th-congress/senate-bill/567",
        "source": "[DEMO DATA]",
    },
    {
        "number": "H.R.890",
        "title": "Immigrant Rights and Due Process Act",
        "congress": 118,
        "type": "HR",
        "latestAction": {"text": "Referred to the Subcommittee on Immigration and Citizenship", "actionDate": "2024-02-10"},
        "url": "https://www.congress.gov/bill/118th-congress/house-bill/890",
        "source": "[DEMO DATA]",
    },
]


class CongressClient:
    def __init__(self):
        self.api_key = os.getenv("CONGRESS_API_KEY", "")
        self.use_demo = os.getenv("USE_DEMO_DATA", "true").lower() == "true" or not self.api_key

    async def search_bills(self, query: str, limit: int = 5) -> list:
        if self.use_demo or not self.api_key:
            logger.info("Congress API: using demo data")
            return DEMO_BILLS[:limit]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{CONGRESS_API_BASE}/bill",
                    params={"query": query, "limit": limit, "api_key": self.api_key, "format": "json"},
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("bills", [])
        except Exception as e:
            logger.error(f"Congress API error: {e}. Falling back to demo data.")
            return DEMO_BILLS[:limit]

    async def get_bill(self, congress: int, bill_type: str, bill_number: str) -> Optional[dict]:
        if self.use_demo or not self.api_key:
            return DEMO_BILLS[0]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{CONGRESS_API_BASE}/bill/{congress}/{bill_type}/{bill_number}",
                    params={"api_key": self.api_key, "format": "json"},
                )
                resp.raise_for_status()
                return resp.json().get("bill")
        except Exception as e:
            logger.error(f"Congress API bill fetch error: {e}")
            return None
