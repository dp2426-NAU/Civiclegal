"""
CivicLegal AI — RAG Pipeline
Hybrid BM25 + vector retrieval with cross-encoder reranking.
Temperature = 0 for factual grounding. LEGAL INFORMATION ONLY.
"""
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are CivicLegal AI, a legal information assistant. "
    "Provide legal INFORMATION only — never legal advice. "
    "Do not create an attorney-client relationship. "
    "Use only the retrieved context provided. "
    "If the context does not contain sufficient information, say so clearly. "
    "Always cite your sources. "
    "End every response with the disclaimer: "
    "'This is general legal information only, not legal advice. Consult a licensed attorney for advice specific to your situation.'"
)

MINIMUM_SIMILARITY_THRESHOLD = 0.50
CHUNK_SIZE = 500
CHUNK_OVERLAP = 75


class RAGPipeline:
    def __init__(self):
        self.vectorstore = None
        self.bm25_retriever = None
        self.reranker = None
        self.llm = None
        self._initialized = False
        self._try_initialize()

    def _try_initialize(self):
        try:
            self._init_llm()
            self._init_vectorstore()
            self._init_reranker()
            self._initialized = True
            logger.info("RAG pipeline fully initialized")
        except Exception as e:
            logger.warning(f"RAG pipeline partial init: {e}")

    def _init_llm(self):
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0,
                openai_api_key=openai_key,
            )
            logger.info("LLM: GPT-4 initialized")
        else:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            try:
                from langchain_community.llms import Ollama
                self.llm = Ollama(model="mistral", base_url=ollama_url, temperature=0)
                logger.info("LLM: Mistral via Ollama initialized")
            except Exception:
                logger.warning("No LLM available — RAG will use demo mode")
                self.llm = None

    def _init_vectorstore(self):
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings

        persist_dir = str(Path(__file__).parent.parent / "data" / "chroma_db")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/msmarco-MiniLM-L-6-v3",
            model_kwargs={"device": "cpu"},
        )
        self.vectorstore = Chroma(
            collection_name="civiclegal_docs",
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        self.embeddings = embeddings
        logger.info("Vector store initialized")

    def _init_reranker(self):
        try:
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Cross-encoder reranker initialized")
        except Exception as e:
            logger.warning(f"Reranker unavailable: {e}")
            self.reranker = None

    def _hybrid_retrieve(self, query: str, k: int = 5) -> list:
        docs = []
        if self.vectorstore:
            try:
                vector_docs = self.vectorstore.similarity_search_with_score(query, k=k)
                docs.extend(vector_docs)
            except Exception as e:
                logger.warning(f"Vector retrieval error: {e}")

        if self.bm25_retriever:
            try:
                bm25_docs = self.bm25_retriever.get_relevant_documents(query)
                for doc in bm25_docs[:k]:
                    docs.append((doc, 0.7))
            except Exception as e:
                logger.warning(f"BM25 retrieval error: {e}")

        return docs

    def _rerank(self, query: str, docs: list) -> list:
        if not docs:
            return []
        if not self.reranker:
            return sorted(docs, key=lambda x: x[1] if isinstance(x[1], float) else 0, reverse=True)
        try:
            pairs = [(query, doc.page_content if hasattr(doc, 'page_content') else str(doc)) for doc, _ in docs]
            scores = self.reranker.predict(pairs)
            reranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
            return [(doc, score) for (doc, _), score in reranked]
        except Exception as e:
            logger.warning(f"Reranking error: {e}")
            return docs

    def _build_context(self, docs: list) -> tuple:
        context_parts = []
        citations = []
        for i, (doc, score) in enumerate(docs[:5]):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            meta = doc.metadata if hasattr(doc, 'metadata') else {}
            context_parts.append(f"[Source {i+1}] {content}")
            citations.append({
                "title": meta.get("title", f"Source {i+1}"),
                "source": meta.get("source", "legal_document"),
                "url": meta.get("url", ""),
                "relevance": float(score) if isinstance(score, (int, float)) else 0.75,
            })
        return "\n\n".join(context_parts), citations

    def query(self, question: str, jurisdiction: str = "federal") -> dict:
        from langchain.schema import HumanMessage, SystemMessage

        if not self._initialized or not self.llm:
            raise RuntimeError("RAG pipeline not available")

        raw_docs = self._hybrid_retrieve(question)
        if not raw_docs:
            return {
                "answer": "Insufficient information in knowledge base to answer this question. Please consult a licensed attorney.",
                "citations": [],
                "confidence": 0.0,
            }

        top_score = raw_docs[0][1] if raw_docs else 0
        if isinstance(top_score, float) and top_score < MINIMUM_SIMILARITY_THRESHOLD:
            return {
                "answer": (
                    "I cannot find sufficiently relevant legal information to answer this question confidently. "
                    "Please consult a licensed attorney or contact Legal Aid in your area."
                ),
                "citations": [],
                "confidence": float(top_score),
            }

        reranked = self._rerank(question, raw_docs)
        context, citations = self._build_context(reranked)
        confidence = float(reranked[0][1]) if reranked else 0.5

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}\nJurisdiction: {jurisdiction}"),
        ]

        response = self.llm(messages)
        answer = response.content if hasattr(response, 'content') else str(response)

        from rag.hallucination_guard import HallucinationGuard
        guard = HallucinationGuard()
        answer, confidence = guard.check(answer, context, confidence)

        return {"answer": answer, "citations": citations, "confidence": confidence}
