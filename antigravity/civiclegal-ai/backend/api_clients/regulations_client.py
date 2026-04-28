"""
CivicLegal AI — Regulations.gov API Client
Fetches federal regulatory documents. Falls back to demo data if unavailable.
DEMO DATA – NOT LEGAL ADVICE
"""
import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

REGULATIONS_API_BASE = "https://api.regulations.gov/v4"
DEMO_REGULATIONS = [
    {
        "id": "HUD-2024-0001",
        "title": "Fair Housing Act Implementation Rules",
        "agencyId": "HUD",
        "documentType": "Rule",
        "postedDate": "2024-01-20",
        "summary": "Updated guidelines for Fair Housing Act enforcement and tenant protections.",
        "url": "https://www.regulations.gov/document/HUD-2024-0001",
        "source": "[DEMO DATA]",
    },
    {
        "id": "DOJ-2024-0045",
        "title": "ADA Title II Regulations Update",
        "agencyId": "DOJ",
        "documentType": "Proposed Rule",
        "postedDate": "2024-02-14",
        "summary": "Proposed updates to ADA Title II accessibility requirements for state and local governments.",
        "url": "https://www.regulations.gov/document/DOJ-2024-0045",
        "source": "[DEMO DATA]",
    },
    {
        "id": "USCIS-2024-0012",
        "title": "Asylum Processing Rule",
        "agencyId": "USCIS",
        "documentType": "Final Rule",
        "postedDate": "2024-03-01",
        "summary": "Final rule establishing procedures for processing asylum applications.",
        "url": "https://www.regulations.gov/document/USCIS-2024-0012",
        "source": "[DEMO DATA]",
    },
]


class RegulationsClient:
    def __init__(self):
        self.api_key = os.getenv("REGULATIONS_API_KEY", "")
        self.use_demo = os.getenv("USE_DEMO_DATA", "true").lower() == "true" or not self.api_key

    async def search_documents(self, query: str, limit: int = 5) -> list:
        if self.use_demo or not self.api_key:
            logger.info("Regulations API: using demo data")
            return DEMO_REGULATIONS[:limit]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{REGULATIONS_API_BASE}/documents",
                    params={
                        "filter[searchTerm]": query,
                        "page[size]": limit,
                        "api_key": self.api_key,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Regulations API error: {e}. Falling back to demo data.")
            return DEMO_REGULATIONS[:limit]

    async def get_document(self, document_id: str) -> Optional[dict]:
        if self.use_demo or not self.api_key:
            return DEMO_REGULATIONS[0]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{REGULATIONS_API_BASE}/documents/{document_id}",
                    params={"api_key": self.api_key},
                )
                resp.raise_for_status()
                return resp.json().get("data")
        except Exception as e:
            logger.error(f"Regulations API fetch error: {e}")
            return None
