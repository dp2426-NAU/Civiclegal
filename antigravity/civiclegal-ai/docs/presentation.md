# CivicLegal AI — 10-Slide Presentation Script

**Project:** CivicLegal AI — AI-Powered Citizen Legal Rights Navigator
**Duration:** ~15 minutes
**Audience:** Technical reviewers, stakeholders, general audience

---

## Slide 1: Title

**CivicLegal AI**
*AI-Powered Citizen Legal Rights & Government Services Navigator*

"Today I'm presenting CivicLegal AI — a RAG-based web application that helps everyday citizens understand their legal rights and find government benefits, in plain language, with cited and grounded responses.

Legal disclaimer: this system provides legal information only, not legal advice."

---

## Slide 2: The Problem

**57 million Americans have civil legal problems each year.
Only 1 in 5 get the help they need.**

- Legal aid organizations are overwhelmed
- Government benefit information is fragmented
- Legal language is inaccessible to most citizens
- Fear and confusion prevent people from asserting their rights

"Whether it's a tenant facing eviction, someone with a disability being denied accommodation, or a family unsure what benefits they qualify for — CivicLegal AI is built for them."

---

## Slide 3: The Solution

**CivicLegal AI: Three Core Capabilities**

1. **Legal Rights Navigator** — Ask any plain-language question about your rights
2. **Benefits Finder** — Enter your household profile, get matched to 10 programs
3. **Document Upload** — Upload legal documents for context-aware analysis

"All responses include citations, confidence scores, and mandatory legal disclaimers. No API keys required — demo mode works out of the box."

---

## Slide 4: System Architecture

[Show system_architecture.svg]

- **Frontend:** Streamlit (4 tabs, sidebar disclaimer)
- **Backend:** FastAPI (3 endpoints: /legal-query, /benefits-match, /upload-document)
- **RAG:** LangChain + ChromaDB + FAISS + BM25
- **LLM:** GPT-4 (primary) → Mistral 7B via Ollama (fallback) → Demo mode
- **Guard:** 5-layer hallucination prevention

---

## Slide 5: RAG Pipeline

[Show rag_flow.svg]

"The retrieval pipeline uses hybrid search — combining BM25 keyword matching with dense vector search — then applies cross-encoder reranking to surface the most relevant legal documents.

Key design choices:
- Chunk size: 500 tokens, 75 overlap
- Minimum similarity threshold: 0.50 (refuse if below)
- Temperature: 0 (deterministic, no creative generation)"

---

## Slide 6: Anti-Hallucination System

[Show hallucination_guard_flow.svg]

**5 Layers of Protection:**

1. Refusal detection — identifies uncertainty signals
2. Grounding check — cosine similarity ≥ 0.50 against retrieved context
3. Overconfidence detection — caps confidence at 0.70
4. Citation validation — filters ungrounded source references
5. Disclaimer injection — mandatory on every single response

"In legal AI, a wrong answer isn't just unhelpful — it can cause real harm. This guard ensures we never fabricate laws, cases, or rights that don't exist."

---

## Slide 7: Benefits Matcher

[Show benefits_matching_flow.svg]

**10 Federal Programs:**
SNAP · Medicaid · CHIP · WIC · TANF · Section 8 · SSI · SSDI · EITC · LIHEAP

**Eligibility factors:**
- 2024 Federal Poverty Level calculations
- Household size and income
- Children, disability, veteran status
- Age requirements

"A family of 3 earning $28,000 takes less than 2 seconds to match. Results include required documents and direct links to apply."

---

## Slide 8: Demo

[Live demo or demo_output.html]

Three scenarios:
1. Tenant rights question → citations from Fair Housing Act
2. Benefits match for family of 3 → SNAP, Medicaid, CHIP eligible
3. Document upload → confirmation and indexing

"Notice that every response carries a confidence badge and the mandatory disclaimer. Demo mode is clearly labeled throughout."

---

## Slide 9: Data Sources & APIs

| Source | Content | Fallback |
|--------|---------|---------|
| CourtListener | Court opinions | Demo cases |
| Congress.gov | Legislation | Demo bills |
| Regulations.gov | Federal regulations | Demo regs |
| Benefits.gov | Benefit programs | Hardcoded data |
| CUAD | Contract analysis | Sample docs |

"All API clients implement graceful degradation. If a key is missing or a service is down, demo data is returned with clear labeling."

---

## Slide 10: Impact & Next Steps

**Current MVP:**
- Full RAG pipeline with anti-hallucination
- 10 federal benefit programs
- Demo mode requiring zero API keys
- Render.com deployment ready

**Potential Impact:**
- Serve underrepresented communities lacking legal access
- Multilingual expansion (Spanish, Chinese, Arabic)
- State-specific law databases
- Integration with local legal aid organizations

"CivicLegal AI is a foundation for making legal information as accessible as a Google search — but grounded, safe, and always with a clear disclaimer."

---

*LEGAL DISCLAIMER: CivicLegal AI provides general legal INFORMATION only — NOT legal advice.*
*Consult a licensed attorney for advice specific to your situation.*
