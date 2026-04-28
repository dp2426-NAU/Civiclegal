"""
CivicLegal AI — Streamlit Frontend
AI-Powered Citizen Legal Rights & Government Services Navigator
LEGAL INFORMATION ONLY — NOT LEGAL ADVICE
"""
import os
import json
import requests
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DISCLAIMER = (
    "⚖️ **LEGAL DISCLAIMER:** CivicLegal AI provides general legal **INFORMATION** only — "
    "**NOT legal advice**. This system does not create an attorney-client relationship. "
    "For advice specific to your situation, **consult a licensed attorney**."
)

st.set_page_config(
    page_title="CivicLegal AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2e6da4 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; }
    .main-header p { margin: 0.3rem 0 0; opacity: 0.85; font-size: 1rem; }
    .disclaimer-box {
        background: #fff8e1;
        border-left: 5px solid #f39c12;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .demo-banner {
        background: #e8f4fd;
        border-left: 5px solid #3498db;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .confidence-high { color: #27ae60; font-weight: bold; }
    .confidence-med  { color: #f39c12; font-weight: bold; }
    .confidence-low  { color: #e74c3c; font-weight: bold; }
    .citation-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.4rem 0;
    }
    .answer-box {
        background: #f0f7ff;
        border-left: 4px solid #2e6da4;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        white-space: pre-wrap;
    }
    .stTabs [data-baseweb="tab"] { font-size: 0.95rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ CivicLegal AI")
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Quick Links")
    st.markdown("- 🏛️ [Legal Aid Locator](https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help)")
    st.markdown("- 📜 [USA.gov Legal Resources](https://www.usa.gov/legal-aid)")
    st.markdown("- 🏥 [Benefits.gov](https://www.benefits.gov)")
    st.markdown("- ⚖️ [ADA.gov](https://www.ada.gov)")
    st.markdown("---")

    backend_status = "🔴 Offline"
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if r.status_code == 200:
            data = r.json()
            backend_status = "🟢 Online (Demo)" if data.get("demo_mode") else "🟢 Online"
    except Exception:
        pass
    st.markdown(f"**Backend:** {backend_status}")
    st.markdown(f"**API:** `{BACKEND_URL}`")


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚖️ CivicLegal AI</h1>
    <p>AI-Powered Citizen Legal Rights & Government Services Navigator</p>
</div>
""", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Legal Rights Navigator",
    "💰 Benefits Finder",
    "📄 Upload Document",
    "ℹ️ About",
])


# ── Tab 1: Legal Rights Navigator ──────────────────────────────────────────────
with tab1:
    st.subheader("Legal Rights Navigator")
    st.markdown("Ask any plain-language question about your legal rights or government services.")

    with st.form("legal_form"):
        question = st.text_area(
            "Your Question",
            placeholder="e.g., What are my rights if my landlord wants to evict me?",
            height=120,
        )
        jurisdiction = st.selectbox(
            "Jurisdiction",
            ["federal", "alabama", "alaska", "arizona", "california", "colorado",
             "florida", "georgia", "illinois", "new york", "texas", "washington"],
            index=0,
        )
        submit = st.form_submit_button("🔍 Ask CivicLegal AI", type="primary")

    if submit and question.strip():
        with st.spinner("Searching legal knowledge base..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/legal-query",
                    json={"question": question.strip(), "jurisdiction": jurisdiction},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()

                if data.get("demo_mode"):
                    st.markdown('<div class="demo-banner">📊 <strong>Demo Mode</strong> — Showing sample data. Connect APIs for live results.</div>', unsafe_allow_html=True)

                # Confidence badge
                conf = data.get("confidence", 0)
                if conf >= 0.80:
                    badge = f'<span class="confidence-high">● High Confidence ({conf:.0%})</span>'
                elif conf >= 0.60:
                    badge = f'<span class="confidence-med">● Medium Confidence ({conf:.0%})</span>'
                else:
                    badge = f'<span class="confidence-low">● Low Confidence ({conf:.0%})</span>'

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("#### Answer")
                with col2:
                    st.markdown(badge, unsafe_allow_html=True)

                st.markdown(f'<div class="answer-box">{data.get("answer", "")}</div>', unsafe_allow_html=True)

                # Citations
                citations = data.get("citations", [])
                if citations:
                    st.markdown("#### 📚 Citations")
                    for i, cit in enumerate(citations, 1):
                        rel = cit.get("relevance", 0)
                        url = cit.get("url", "")
                        link = f'<a href="{url}" target="_blank">🔗 View Source</a>' if url else ""
                        st.markdown(
                            f'<div class="citation-card">'
                            f'<strong>[{i}] {cit.get("title", "Source")}</strong><br>'
                            f'Source: {cit.get("source", "—")} | Relevance: {rel:.0%} {link}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                st.markdown(f'<div class="disclaimer-box">{data.get("disclaimer", "")}</div>', unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"Error: {e}")

    elif submit:
        st.warning("Please enter a question.")


# ── Tab 2: Benefits Finder ─────────────────────────────────────────────────────
with tab2:
    st.subheader("Benefits Finder")
    st.markdown("Find government benefit programs you may qualify for based on your situation.")

    with st.form("benefits_form"):
        col1, col2 = st.columns(2)
        with col1:
            household_size = st.number_input("Household Size (persons)", min_value=1, max_value=20, value=3)
            annual_income = st.number_input("Annual Household Income ($)", min_value=0, max_value=500000, value=28000, step=1000)
            age = st.number_input("Your Age", min_value=0, max_value=120, value=35)
        with col2:
            state = st.selectbox("State", [
                "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
                "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
                "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
                "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
                "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
                "New Hampshire", "New Jersey", "New Mexico", "New York",
                "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
                "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
                "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
                "West Virginia", "Wisconsin", "Wyoming",
            ], index=4)
            has_children = st.checkbox("Household includes dependent children")
            has_disability = st.checkbox("Household member has a documented disability")
            is_veteran = st.checkbox("Household member is a veteran")

        submit_benefits = st.form_submit_button("🔎 Find My Benefits", type="primary")

    if submit_benefits:
        with st.spinner("Matching benefit programs..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/benefits-match",
                    json={
                        "household_size": int(household_size),
                        "annual_income": float(annual_income),
                        "state": state,
                        "has_children": has_children,
                        "has_disability": has_disability,
                        "is_veteran": is_veteran,
                        "age": int(age),
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

                if data.get("demo_mode"):
                    st.markdown('<div class="demo-banner">📊 <strong>Demo Mode</strong> — Eligibility based on federal guidelines.</div>', unsafe_allow_html=True)

                programs = data.get("programs", [])
                eligible = [p for p in programs if p.get("eligibility")]
                not_eligible = [p for p in programs if not p.get("eligibility")]

                st.markdown(f"### Found **{len(eligible)}** potentially eligible program(s)")

                for prog in eligible:
                    with st.expander(f"✅ {prog['program']}", expanded=True):
                        st.markdown(f"**{prog.get('description', '')}**")
                        st.markdown(f"📋 **Why you may qualify:** {prog.get('reason', '')}")
                        st.markdown(f"🏛️ **Agency:** {prog.get('agency', '')}")
                        docs = prog.get("documents_needed", [])
                        if docs:
                            st.markdown("**Documents You May Need:**")
                            for doc in docs:
                                st.markdown(f"  - {doc}")
                        link = prog.get("link", "")
                        if link:
                            st.markdown(f"[🔗 Apply or Learn More]({link})")
                        if prog.get("demo_label"):
                            st.caption(prog["demo_label"])

                if not_eligible:
                    with st.expander("Programs you may not qualify for"):
                        for prog in not_eligible:
                            st.markdown(f"❌ **{prog['program']}** — {prog.get('reason', '')}")

                st.markdown(f'<div class="disclaimer-box">{data.get("disclaimer", "")}</div>', unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"Error: {e}")


# ── Tab 3: Upload Document ─────────────────────────────────────────────────────
with tab3:
    st.subheader("Upload Legal Document")
    st.markdown("Upload a legal document for analysis. Supported: **PDF, DOCX, TXT** (max 10 MB).")

    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        if st.button("📤 Upload & Analyze", type="primary"):
            with st.spinner("Uploading document..."):
                try:
                    content_type_map = {
                        "pdf": "application/pdf",
                        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "txt": "text/plain",
                    }
                    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                    ct = content_type_map.get(ext, "application/octet-stream")

                    resp = requests.post(
                        f"{BACKEND_URL}/upload-document",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), ct)},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    st.success(f"✅ {data.get('message', 'Upload successful!')}")
                    st.info(f"📁 File: **{data.get('filename')}** | Size: {data.get('size_bytes', 0):,} bytes")
                    if data.get("demo_mode"):
                        st.markdown('<div class="demo-banner">📊 Demo mode — document indexed in demo store.</div>', unsafe_allow_html=True)
                    st.info(data.get("note", ""))
                    st.markdown(f'<div class="disclaimer-box">{data.get("disclaimer", "")}</div>', unsafe_allow_html=True)

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")
                except Exception as e:
                    st.error(f"Upload error: {e}")


# ── Tab 4: About ───────────────────────────────────────────────────────────────
with tab4:
    st.subheader("About CivicLegal AI")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**CivicLegal AI** is an open-source, AI-powered citizen legal rights and government services navigator.

### What It Does
- Answers plain-language legal rights questions
- Matches users to government benefit programs
- Provides grounded citations from federal legal sources
- Operates with an anti-hallucination safeguard system

### Technology
- **Frontend:** Streamlit
- **Backend:** FastAPI
- **RAG:** LangChain + ChromaDB + FAISS
- **LLM:** GPT-4 (or Mistral via Ollama)
- **Embeddings:** msmarco-MiniLM-L-6-v2
- **Reranker:** ms-marco cross-encoder

### Data Sources
- CourtListener (federal case law)
- Congress.gov (legislation)
- Regulations.gov (federal regulations)
- Benefits.gov (government programs)
- CUAD dataset (contract analysis)
""")
    with col2:
        st.markdown("""
### Legal Disclaimer
This system provides **general legal information only** — NOT legal advice. Always consult a licensed attorney for advice specific to your situation.

### Anti-Hallucination Features
1. Temperature = 0 (deterministic outputs)
2. Constrained system prompt
3. Citation verification
4. Grounding similarity check (min 50%)
5. Confidence scoring
6. Overconfidence detection

### Get Help
- 🏛️ [Find Legal Aid](https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help)
- 📞 [Law Help](https://lawhelp.org)
- 🏥 [Benefits.gov](https://www.benefits.gov)
- 🌐 [USA.gov Legal](https://www.usa.gov/legal-aid)

### GitHub
[github.com/dp2426-NAU/Civiclegal](https://github.com/dp2426-NAU/Civiclegal)
""")

    st.markdown("---")
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>', unsafe_allow_html=True)
