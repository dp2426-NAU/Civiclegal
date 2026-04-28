"""
CivicLegal AI — CourtListener API Client
Fetches case law and court opinions. Falls back to demo data if unavailable.
DEMO DATA – NOT LEGAL ADVICE
"""
import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

COURTLISTENER_API_BASE = "https://www.courtlistener.com/api/rest/v3"
DEMO_CASES = [
    {
        "id": "miranda_v_arizona",
        "caseName": "Miranda v. Arizona",
        "court": "U.S. Supreme Court",
        "dateFiled": "1966-06-13",
        "citation": "384 U.S. 436 (1966)",
        "snippet": "The prosecution may not use statements, whether exculpatory or inculpatory, stemming from custodial interrogation of the defendant unless it demonstrates the use of procedural safeguards effective to secure the privilege against self-incrimination.",
        "absoluteUrl": "https://www.courtlistener.com/opinion/107102/miranda-v-arizona/",
        "source": "[DEMO DATA]",
    },
    {
        "id": "brown_v_board",
        "caseName": "Brown v. Board of Education",
        "court": "U.S. Supreme Court",
        "dateFiled": "1954-05-17",
        "citation": "347 U.S. 483 (1954)",
        "snippet": "Separate educational facilities are inherently unequal, violating the Equal Protection Clause of the Fourteenth Amendment.",
        "absoluteUrl": "https://www.courtlistener.com/opinion/105614/brown-v-board-of-education/",
        "source": "[DEMO DATA]",
    },
    {
        "id": "obergefell_v_hodges",
        "caseName": "Obergefell v. Hodges",
        "court": "U.S. Supreme Court",
        "dateFiled": "2015-06-26",
        "citation": "576 U.S. 644 (2015)",
        "snippet": "The Fourteenth Amendment requires a State to license a marriage between two people of the same sex and to recognize a marriage between two people of the same sex when their marriage was lawfully licensed and performed out-of-State.",
        "absoluteUrl": "https://www.courtlistener.com/opinion/2812209/obergefell-v-hodges/",
        "source": "[DEMO DATA]",
    },
]


class CourtListenerClient:
    def __init__(self):
        self.api_key = os.getenv("COURTLISTENER_API_KEY", "")
        self.use_demo = os.getenv("USE_DEMO_DATA", "true").lower() == "true" or not self.api_key

    def _headers(self) -> dict:
        if self.api_key:
            return {"Authorization": f"Token {self.api_key}"}
        return {}

    async def search_opinions(self, query: str, limit: int = 5) -> list:
        if self.use_demo or not self.api_key:
            logger.info("CourtListener API: using demo data")
            return DEMO_CASES[:limit]
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{COURTLISTENER_API_BASE}/search/",
                    params={"q": query, "type": "o", "order_by": "score desc", "page_size": limit},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"CourtListener API error: {e}. Falling back to demo data.")
            return DEMO_CASES[:limit]

    async def get_opinion(self, opinion_id: int) -> Optional[dict]:
        if self.use_demo or not self.api_key:
            return DEMO_CASES[0]
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{COURTLISTENER_API_BASE}/opinions/{opinion_id}/",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"CourtListener opinion fetch error: {e}")
            return None
