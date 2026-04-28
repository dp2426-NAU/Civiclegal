"""
CivicLegal AI — Hallucination Guard
Multi-layer anti-hallucination system for legal information outputs.
"""
import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

MINIMUM_SIMILARITY = 0.50
CONFIDENCE_PENALTY_THRESHOLD = 0.65

REFUSAL_PHRASES = [
    "i cannot", "i don't know", "i'm not sure",
    "insufficient information", "i do not have",
    "cannot find", "no relevant information",
]

HALLUCINATION_RISK_PHRASES = [
    "definitely", "absolutely certain", "guaranteed", "always wins",
    "you will win", "100%", "without a doubt", "the court will",
    "the judge will", "you are certain to",
]

DISCLAIMER_REQUIRED = (
    "This is general legal information only, not legal advice. "
    "Consult a licensed attorney for advice specific to your situation."
)


class HallucinationGuard:
    def __init__(self):
        self.similarity_model = None
        self._try_load_model()

    def _try_load_model(self):
        try:
            from sentence_transformers import SentenceTransformer, util
            self.similarity_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self._util = util
            logger.info("Hallucination guard similarity model loaded")
        except Exception as e:
            logger.warning(f"Similarity model unavailable: {e}")

    def check_similarity(self, answer: str, context: str) -> float:
        if not self.similarity_model or not context:
            return 0.75
        try:
            emb_a = self.similarity_model.encode(answer, convert_to_tensor=True)
            emb_c = self.similarity_model.encode(context[:2000], convert_to_tensor=True)
            score = float(self._util.cos_sim(emb_a, emb_c).item())
            return max(0.0, min(1.0, score))
        except Exception as e:
            logger.warning(f"Similarity check error: {e}")
            return 0.75

    def detect_overconfidence(self, answer: str) -> list:
        flags = []
        answer_lower = answer.lower()
        for phrase in HALLUCINATION_RISK_PHRASES:
            if phrase in answer_lower:
                flags.append(phrase)
        return flags

    def is_refusal(self, answer: str) -> bool:
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)

    def ensure_disclaimer(self, answer: str) -> str:
        if DISCLAIMER_REQUIRED.lower()[:30] not in answer.lower():
            return answer + f"\n\n{DISCLAIMER_REQUIRED}"
        return answer

    def check(self, answer: str, context: str, initial_confidence: float) -> Tuple[str, float]:
        confidence = initial_confidence

        if self.is_refusal(answer):
            answer = self.ensure_disclaimer(answer)
            return answer, max(0.0, confidence * 0.5)

        sim_score = self.check_similarity(answer, context)
        if sim_score < MINIMUM_SIMILARITY:
            logger.warning(f"Low grounding score: {sim_score:.3f} — refusing answer")
            safe_answer = (
                f"I cannot provide a well-grounded answer to this question based on the available legal documents. "
                f"Grounding score: {sim_score:.2f} (minimum required: {MINIMUM_SIMILARITY}).\n\n"
                f"Please consult a licensed attorney or contact Legal Aid in your jurisdiction.\n\n"
                f"{DISCLAIMER_REQUIRED}"
            )
            return safe_answer, sim_score

        if sim_score < CONFIDENCE_PENALTY_THRESHOLD:
            confidence = confidence * (0.5 + sim_score * 0.5)
            logger.info(f"Confidence adjusted to {confidence:.3f} due to low grounding ({sim_score:.3f})")

        overconfident_flags = self.detect_overconfidence(answer)
        if overconfident_flags:
            logger.warning(f"Overconfidence detected: {overconfident_flags}")
            warning = (
                "\n\n⚠️ Note: Legal outcomes vary significantly by jurisdiction and individual circumstances. "
                "No legal outcome can be guaranteed."
            )
            answer = answer + warning
            confidence = min(confidence, 0.70)

        answer = self.ensure_disclaimer(answer)
        return answer, min(1.0, max(0.0, confidence))

    def validate_citations(self, citations: list, answer: str) -> list:
        validated = []
        for citation in citations:
            title = citation.get("title", "")
            if not title:
                continue
            key_terms = re.findall(r'\b[A-Z][a-z]+\b', title)
            cited_in_answer = any(term.lower() in answer.lower() for term in key_terms[:3]) if key_terms else True
            if cited_in_answer or citation.get("relevance", 0) > 0.7:
                validated.append(citation)
            else:
                logger.info(f"Citation filtered (not grounded in answer): {title}")
        return validated
