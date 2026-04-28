# CivicLegal AI — Project Proposal

**Project Title:** CivicLegal AI — AI-Powered Citizen Legal Rights & Government Services Navigator
**Repository:** https://github.com/dp2426-NAU/Civiclegal
**Date:** April 2026

---

## Executive Summary

CivicLegal AI is a Retrieval-Augmented Generation (RAG) web application that helps citizens navigate their legal rights and government benefit programs using plain-language queries. The system provides grounded, cited legal **information** (not advice) through a 5-layer anti-hallucination pipeline, making legal knowledge accessible to underserved communities.

---

## Problem Statement

The United States faces a significant "legal gap":
- 57 million Americans experience civil legal problems annually
- Only ~20% receive adequate legal assistance
- Legal information is buried in court databases, federal registers, and government portals
- Legal language is inaccessible to most citizens

---

## Proposed Solution

A RAG-based web application featuring:
1. Plain-language legal question answering
2. Automated government benefit eligibility matching
3. Document upload and contextual analysis
4. Citation-backed, grounded responses with confidence scoring
5. Mandatory disclaimers and anti-hallucination safeguards

---

## Technical Approach

### Architecture
- Frontend: Streamlit
- Backend: FastAPI
- RAG: LangChain + ChromaDB + FAISS + BM25 hybrid retrieval
- LLM: GPT-4 / Mistral 7B
- Embeddings: msmarco-MiniLM-L-6-v2
- Reranker: ms-marco cross-encoder

### Data Sources
- CourtListener (federal case law)
- Congress.gov (legislation)
- Regulations.gov (regulations)
- Benefits.gov (benefit programs)
- CUAD dataset

### Safety Measures
- Temperature = 0
- Constrained system prompt
- 5-layer hallucination guard
- Minimum similarity threshold (0.50)
- Mandatory disclaimer on every response

---

## Expected Outcomes

1. Functional MVP deployed on Render.com
2. Demo mode working without API keys
3. Benefits matching for 10 federal programs
4. Legal RAG pipeline with anti-hallucination
5. Complete documentation and test suite

---

## Legal & Ethical Compliance

- System explicitly provides information, never advice
- No attorney-client relationship created
- All AI-generated content labeled with confidence scores
- Demo data clearly marked
- Users directed to licensed attorneys and legal aid organizations

---

## Timeline

| Phase | Duration | Deliverable |
|-------|---------|------------|
| Architecture Design | Week 1 | System diagram, API spec |
| Backend Development | Week 2 | FastAPI endpoints, benefits matcher |
| RAG Pipeline | Week 3 | ChromaDB, hybrid retrieval, reranker |
| Frontend | Week 4 | Streamlit UI, all 4 tabs |
| Anti-Hallucination | Week 5 | 5-layer guard system |
| Testing & Docs | Week 6 | pytest suite, full documentation |
| Deployment | Week 7 | Render.com, GitHub push |

---

*LEGAL DISCLAIMER: This proposal describes a system that provides legal information only — NOT legal advice.*
