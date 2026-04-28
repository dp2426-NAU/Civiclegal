# CivicLegal AI — Technical Documentation

**Version:** 1.0.0
**Date:** April 2026
**Status:** MVP — Production Ready

> **LEGAL DISCLAIMER:** CivicLegal AI provides general legal INFORMATION only — NOT legal advice.

---

## 1. Project Overview

CivicLegal AI is an AI-powered citizen legal rights and government services navigator. It uses Retrieval-Augmented Generation (RAG) to answer plain-language legal questions with grounded, cited responses drawn from federal legal sources.

### 1.1 Core Objectives

- Democratize access to legal information for underserved communities
- Provide grounded, cited answers — never hallucinated content
- Match users to government benefit programs automatically
- Operate safely without API keys via demo mode

### 1.2 Problem Statement

Legal information is fragmented across court databases, government portals, and statutes — inaccessible to most citizens. CivicLegal AI aggregates and surfaces this information through a natural language interface.

---

## 2. System Architecture

### 2.1 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit 1.36 | Web UI with 4 tabs |
| Backend | FastAPI 0.111 | REST API, business logic |
| RAG | LangChain 0.2 | RAG orchestration |
| Vector DB | ChromaDB 0.5 | Semantic search |
| Sparse Index | FAISS 1.8 | ANN search |
| BM25 | rank-bm25 0.2 | Keyword retrieval |
| Embeddings | msmarco-MiniLM-L-6-v2 | Dense representations |
| Reranker | ms-marco cross-encoder | Result reranking |
| LLM (primary) | GPT-4 | Text generation |
| LLM (fallback) | Mistral 7B / Ollama | Local inference |
| Doc parsing | PyMuPDF, python-docx | PDF/DOCX ingestion |

### 2.2 Component Breakdown

**Frontend (`frontend/app.py`)**
- Streamlit application with sidebar disclaimer
- Tab 1: Legal Rights Navigator with jurisdiction selector
- Tab 2: Benefits Finder with household profile form
- Tab 3: Document upload with drag-and-drop
- Tab 4: About page with architecture details
- Confidence badge (color-coded: High/Medium/Low)
- Citation cards with clickable source links

**Backend (`backend/main.py`)**
- FastAPI with CORS middleware
- `GET /health` — system status
- `POST /legal-query` — RAG + LLM query
- `POST /benefits-match` — eligibility engine
- `POST /upload-document` — document ingestion
- Automatic demo mode fallback on all endpoints

**RAG Pipeline (`rag/rag_pipeline.py`)**
- Hybrid retrieval: BM25 keyword + vector semantic search
- Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
- LangChain orchestration with constrained system prompt
- Temperature = 0 for deterministic outputs

**Hallucination Guard (`rag/hallucination_guard.py`)**
Five verification layers:
1. Refusal detection → confidence penalty
2. Grounding similarity check (cosine ≥ 0.50)
3. Overconfidence phrase detection → confidence cap
4. Citation validation against answer content
5. Mandatory disclaimer injection

**Benefits Matcher (`backend/benefits_matcher.py`)**
- 2024 Federal Poverty Level (FPL) calculations
- 10 programs: SNAP, Medicaid, CHIP, WIC, TANF, Section 8, SSI, SSDI, EITC, LIHEAP
- Multi-dimensional eligibility: income, children, disability, age, veteran status

---

## 3. RAG Pipeline Details

### 3.1 Document Ingestion

```
PDF / DOCX / TXT → PyMuPDF/python-docx
  → Text extraction
  → Chunking (500 tokens, 75 overlap)
  → msmarco-MiniLM-L6 embeddings
  → ChromaDB (vector store)
  → FAISS (ANN index)
  → BM25 (sparse index)
```

### 3.2 Retrieval

```
User query
  → BM25 keyword retrieval (top-K candidates)
  → Vector semantic search (ChromaDB, top-K)
  → Score fusion
  → Cross-encoder reranking (ms-marco)
  → Top-5 context documents
```

### 3.3 Generation

```
System prompt (constrained) + Context + Question
  → LLM (GPT-4 / Mistral / Demo)
  → Temperature = 0
  → Raw answer
  → Hallucination Guard (5 layers)
  → Grounded answer + citations + confidence + disclaimer
```

### 3.4 System Prompt

```
"You are CivicLegal AI, a legal information assistant.
Provide legal INFORMATION only — never legal advice.
Do not create an attorney-client relationship.
Use only the retrieved context provided.
If the context does not contain sufficient information, say so clearly.
Always cite your sources.
End every response with the disclaimer:
'This is general legal information only, not legal advice.
Consult a licensed attorney for advice specific to your situation.'"
```

---

## 4. API Reference

### GET /health

Returns system status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "service": "CivicLegal AI",
  "version": "1.0.0",
  "demo_mode": true,
  "disclaimer": "LEGAL DISCLAIMER: ..."
}
```

### POST /legal-query

**Request:**
```json
{
  "question": "What are my rights as a tenant?",
  "jurisdiction": "federal",
  "max_results": 5
}
```

**Response:**
```json
{
  "answer": "...",
  "citations": [{"title": "...", "source": "...", "url": "...", "relevance": 0.92}],
  "confidence": 0.87,
  "disclaimer": "...",
  "demo_mode": true
}
```

### POST /benefits-match

**Request:**
```json
{
  "household_size": 3,
  "annual_income": 28000,
  "state": "California",
  "has_children": true,
  "has_disability": false,
  "is_veteran": false,
  "age": 35
}
```

**Response:**
```json
{
  "programs": [
    {
      "program": "SNAP",
      "eligibility": true,
      "reason": "Income at 90% of FPL meets 130% threshold",
      "documents_needed": ["Photo ID", "Proof of income"],
      "link": "https://www.fns.usda.gov/snap/eligibility",
      "agency": "USDA"
    }
  ],
  "disclaimer": "...",
  "demo_mode": true
}
```

---

## 5. Data Sources

| Source | API/Dataset | Content |
|--------|------------|---------|
| CourtListener | REST API | Federal court opinions |
| Congress.gov | REST API | Legislation (118th Congress) |
| Regulations.gov | REST API | Federal regulations |
| Benefits.gov | Dataset | Benefit program data |
| CUAD | HuggingFace | Contract analysis |
| Sample docs | Included | Demo legal documents |

All sources fall back to clearly labeled demo data when API keys are absent.

---

## 6. Anti-Hallucination System

The 5-layer hallucination guard prevents the system from generating fabricated legal information:

| Layer | Check | Action on Failure |
|-------|-------|------------------|
| 1 | Refusal detection | Confidence × 0.5 |
| 2 | Grounding similarity ≥ 0.50 | Return safe refusal |
| 3 | Overconfidence phrases | Cap confidence at 0.70 |
| 4 | Citation validation | Filter ungrounded citations |
| 5 | Disclaimer presence | Inject mandatory disclaimer |

---

## 7. Deployment

### Local

```bash
# Backend
uvicorn backend.main:app --reload --port 8000

# Frontend
streamlit run frontend/app.py
```

### Render.com

The included `render.yaml` deploys both services automatically:
- Backend: FastAPI on port 8000
- Frontend: Streamlit connected to backend URL

---

## 8. Testing

```bash
pytest tests/ -v
```

Test coverage:
- Health endpoint validation
- Benefits matcher eligibility logic
- Hallucination guard all 5 layers
- Disclaimer presence on all responses

---

## 9. Legal & Ethical Considerations

- This system provides **information** only, never **advice**
- No attorney-client relationship is created
- Demo data is clearly labeled
- Temperature = 0 prevents creative hallucination
- Minimum similarity threshold prevents low-grounding responses
- Users are always directed to licensed attorneys for specific advice
