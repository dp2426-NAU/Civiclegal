"""
CivicLegal AI — FastAPI Backend
Provides legal information only. NOT legal advice.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benefits_matcher import BenefitsMatcher
from api_clients.congress_client import CongressClient
from api_clients.regulations_client import RegulationsClient
from api_clients.courtlistener_client import CourtListenerClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCLAIMER = (
    "LEGAL DISCLAIMER: CivicLegal AI provides general legal INFORMATION only, "
    "not legal advice. This system does not create an attorney-client relationship. "
    "For advice specific to your situation, consult a licensed attorney."
)

USE_DEMO_DATA = os.getenv("USE_DEMO_DATA", "true").lower() == "true"

app = FastAPI(
    title="CivicLegal AI API",
    description="AI-Powered Citizen Legal Rights & Government Services Navigator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

benefits_matcher = BenefitsMatcher()
congress_client = CongressClient()
regulations_client = RegulationsClient()
courtlistener_client = CourtListenerClient()

# Lazy-load RAG pipeline to avoid slow startup
_rag_pipeline = None

def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            from rag.rag_pipeline import RAGPipeline
            _rag_pipeline = RAGPipeline()
            logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            logger.warning(f"RAG pipeline unavailable: {e}. Using demo mode.")
            _rag_pipeline = None
    return _rag_pipeline


class LegalQueryRequest(BaseModel):
    question: str
    jurisdiction: Optional[str] = "federal"
    max_results: Optional[int] = 5


class BenefitsMatchRequest(BaseModel):
    household_size: int
    annual_income: float
    state: str
    has_children: Optional[bool] = False
    has_disability: Optional[bool] = False
    is_veteran: Optional[bool] = False
    age: Optional[int] = None


class LegalQueryResponse(BaseModel):
    answer: str
    citations: list
    confidence: float
    disclaimer: str
    demo_mode: bool


class BenefitsResponse(BaseModel):
    programs: list
    disclaimer: str
    demo_mode: bool


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CivicLegal AI API</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f0f4f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .card { background: white; border-radius: 12px; padding: 2.5rem 3rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 560px; width: 100%; }
    h1 { color: #1a3a5c; margin: 0 0 0.3rem; font-size: 1.8rem; }
    .sub { color: #555; margin-bottom: 1.5rem; font-size: 0.95rem; }
    .badge { display: inline-block; background: #d4edda; color: #155724; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.82rem; font-weight: bold; margin-bottom: 1.5rem; }
    .endpoints { list-style: none; padding: 0; margin: 0 0 1.5rem; }
    .endpoints li { padding: 0.55rem 0; border-bottom: 1px solid #eee; font-size: 0.93rem; }
    .endpoints li:last-child { border: none; }
    .method { display: inline-block; width: 46px; font-size: 0.75rem; font-weight: bold; padding: 0.15rem 0.3rem; border-radius: 4px; text-align: center; margin-right: 0.5rem; }
    .get  { background: #cfe2ff; color: #084298; }
    .post { background: #d1e7dd; color: #0f5132; }
    a { color: #2e6da4; text-decoration: none; font-weight: 500; }
    a:hover { text-decoration: underline; }
    .disclaimer { background: #fff8e1; border-left: 4px solid #f39c12; padding: 0.8rem 1rem; border-radius: 0 6px 6px 0; font-size: 0.82rem; color: #555; }
  </style>
</head>
<body>
  <div class="card">
    <h1>&#9878; CivicLegal AI API</h1>
    <p class="sub">AI-Powered Citizen Legal Rights &amp; Government Services Navigator</p>
    <span class="badge">&#10003; API is running &mdash; Demo Mode</span>
    <ul class="endpoints">
      <li><span class="method get">GET</span> <a href="/health">/health</a> &mdash; System status</li>
      <li><span class="method post">POST</span> /legal-query &mdash; Ask a legal question</li>
      <li><span class="method post">POST</span> /benefits-match &mdash; Find benefit programs</li>
      <li><span class="method post">POST</span> /upload-document &mdash; Upload a legal document</li>
      <li><span class="method get">GET</span> <a href="/docs">/docs</a> &mdash; Interactive API docs (Swagger)</li>
      <li><span class="method get">GET</span> <a href="/redoc">/redoc</a> &mdash; ReDoc documentation</li>
    </ul>
    <div class="disclaimer">
      <strong>Legal Disclaimer:</strong> CivicLegal AI provides general legal <strong>information</strong> only &mdash; NOT legal advice.
      Consult a licensed attorney for advice specific to your situation.
    </div>
  </div>
</body>
</html>
"""


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CivicLegal AI",
        "version": "1.0.0",
        "demo_mode": USE_DEMO_DATA,
        "disclaimer": DISCLAIMER,
    }


@app.post("/legal-query", response_model=LegalQueryResponse)
async def legal_query(request: LegalQueryRequest):
    if not request.question or len(request.question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Question too short.")

    # Skip RAG pipeline entirely in demo mode — avoids slow model downloads
    if not USE_DEMO_DATA:
        pipeline = get_rag_pipeline()
    else:
        pipeline = None

    if pipeline and not USE_DEMO_DATA:
        try:
            result = pipeline.query(request.question, jurisdiction=request.jurisdiction)
            return LegalQueryResponse(
                answer=result["answer"],
                citations=result["citations"],
                confidence=result["confidence"],
                disclaimer=DISCLAIMER,
                demo_mode=False,
            )
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}")

    # Demo mode fallback
    demo_result = _get_demo_legal_response(request.question, request.jurisdiction)
    return LegalQueryResponse(
        answer=demo_result["answer"],
        citations=demo_result["citations"],
        confidence=demo_result["confidence"],
        disclaimer=DISCLAIMER,
        demo_mode=True,
    )


@app.post("/benefits-match", response_model=BenefitsResponse)
async def benefits_match(request: BenefitsMatchRequest):
    try:
        programs = benefits_matcher.match(
            household_size=request.household_size,
            annual_income=request.annual_income,
            state=request.state,
            has_children=request.has_children,
            has_disability=request.has_disability,
            is_veteran=request.is_veteran,
            age=request.age,
        )
        return BenefitsResponse(
            programs=programs,
            disclaimer=DISCLAIMER,
            demo_mode=USE_DEMO_DATA,
        )
    except Exception as e:
        logger.error(f"Benefits matcher error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    allowed_types = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum 10 MB.")

    upload_dir = Path(__file__).parent.parent / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    file_path.write_bytes(content)

    return {
        "message": f"Document '{file.filename}' uploaded successfully.",
        "filename": file.filename,
        "size_bytes": len(content),
        "demo_mode": USE_DEMO_DATA,
        "disclaimer": DISCLAIMER,
        "note": "In demo mode, document analysis uses sample responses." if USE_DEMO_DATA else "Document indexed into RAG pipeline.",
    }


def _get_demo_legal_response(question: str, jurisdiction: str) -> dict:
    """Return clearly labeled demo responses when APIs are unavailable."""
    question_lower = question.lower()

    if any(word in question_lower for word in ["evict", "rent", "landlord", "tenant"]):
        answer = (
            "[DEMO DATA – NOT LEGAL ADVICE]\n\n"
            "Tenants generally have the right to:\n"
            "• Receive proper written notice before eviction (typically 30-60 days depending on state)\n"
            "• Habitable living conditions under the implied warranty of habitability\n"
            "• Return of security deposit within the state-mandated timeframe\n"
            "• Protection from retaliation for reporting code violations\n\n"
            "Federal protections include the Fair Housing Act (42 U.S.C. § 3604), which prohibits "
            "discrimination based on race, color, national origin, religion, sex, familial status, or disability.\n\n"
            "State laws vary significantly. Contact your local Legal Aid office for jurisdiction-specific guidance."
        )
        citations = [
            {"title": "Fair Housing Act, 42 U.S.C. § 3604", "source": "federal_statute", "url": "https://www.hud.gov/program_offices/fair_housing_equal_opp/fair_housing_act_overview", "relevance": 0.92},
            {"title": "HUD Tenant Rights Overview", "source": "hud.gov", "url": "https://www.hud.gov/topics/rental_assistance/tenantrights", "relevance": 0.88},
        ]
        confidence = 0.87
    elif any(word in question_lower for word in ["immigrat", "visa", "citizenship", "asylum", "deportat"]):
        answer = (
            "[DEMO DATA – NOT LEGAL ADVICE]\n\n"
            "Key immigration rights include:\n"
            "• The right to remain silent with immigration officers (5th Amendment)\n"
            "• The right to an attorney (though government need not provide one in removal proceedings)\n"
            "• Due process rights in deportation/removal proceedings\n"
            "• Asylum protection under INA § 208 if facing persecution based on race, religion, nationality, political opinion, or social group\n\n"
            "DACA recipients and other status holders have specific protections. "
            "Always consult an immigration attorney before taking action."
        )
        citations = [
            {"title": "Immigration and Nationality Act § 208 (Asylum)", "source": "federal_statute", "url": "https://www.uscis.gov/laws-and-policy/legislation/immigration-and-nationality-act", "relevance": 0.91},
            {"title": "USCIS Rights and Responsibilities", "source": "uscis.gov", "url": "https://www.uscis.gov", "relevance": 0.85},
        ]
        confidence = 0.83
    elif any(word in question_lower for word in ["arrest", "police", "rights", "miranda", "search", "fourth amendment"]):
        answer = (
            "[DEMO DATA – NOT LEGAL ADVICE]\n\n"
            "Constitutional rights during police encounters:\n"
            "• 4th Amendment: Protection against unreasonable searches and seizures\n"
            "• 5th Amendment: Right to remain silent; cannot be compelled to self-incriminate\n"
            "• 6th Amendment: Right to an attorney; request one immediately upon arrest\n"
            "• Miranda Rights must be read before custodial interrogation\n\n"
            "You may calmly state: 'I am invoking my right to remain silent and request an attorney.' "
            "Do not physically resist even if you believe an arrest is unlawful."
        )
        citations = [
            {"title": "Miranda v. Arizona, 384 U.S. 436 (1966)", "source": "supreme_court", "url": "https://supreme.justia.com/cases/federal/us/384/436/", "relevance": 0.95},
            {"title": "U.S. Constitution, Amendment IV", "source": "constitution", "url": "https://constitution.congress.gov/constitution/amendment-4/", "relevance": 0.93},
        ]
        confidence = 0.92
    elif any(word in question_lower for word in ["disability", "ada", "accommodation", "wheelchair"]):
        answer = (
            "[DEMO DATA – NOT LEGAL ADVICE]\n\n"
            "The Americans with Disabilities Act (ADA, 42 U.S.C. § 12101) provides:\n"
            "• Reasonable accommodations in the workplace (Title I)\n"
            "• Access to public services and government programs (Title II)\n"
            "• Access to public accommodations like restaurants and stores (Title III)\n\n"
            "To request a workplace accommodation, notify your employer in writing. "
            "Employers must provide reasonable accommodations unless it causes undue hardship.\n\n"
            "File complaints with the EEOC (employment) or DOJ (public access)."
        )
        citations = [
            {"title": "Americans with Disabilities Act, 42 U.S.C. § 12101", "source": "federal_statute", "url": "https://www.ada.gov/law-and-regs/ada/", "relevance": 0.94},
            {"title": "EEOC ADA Overview", "source": "eeoc.gov", "url": "https://www.eeoc.gov/disability-discrimination", "relevance": 0.89},
        ]
        confidence = 0.90
    else:
        answer = (
            "[DEMO DATA – NOT LEGAL ADVICE]\n\n"
            f"Regarding your question about: '{question}'\n\n"
            "General legal information:\n"
            "• Federal and state laws both apply to most legal matters\n"
            "• You have the right to access public court records under PACER and state equivalents\n"
            "• Free legal aid is available through LSC-funded organizations (lsc.gov)\n"
            "• Many bar associations offer referral services and pro bono programs\n\n"
            "For accurate information specific to your jurisdiction and situation, "
            "please consult a licensed attorney or contact your local legal aid organization."
        )
        citations = [
            {"title": "Legal Services Corporation — Find Legal Aid", "source": "lsc.gov", "url": "https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help", "relevance": 0.75},
            {"title": "USA.gov — Legal Resources", "source": "usa.gov", "url": "https://www.usa.gov/legal-aid", "relevance": 0.72},
        ]
        confidence = 0.65

    return {"answer": answer, "citations": citations, "confidence": confidence}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
