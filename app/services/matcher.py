"""
Semantic FAQ matching engine.

Uses sentence-transformers to encode questions into dense vectors, then finds
the most similar FAQ entry using cosine similarity.

Key design choices
──────────────────
* The model is loaded ONCE at startup (injected via constructor) and reused for
  every request, keeping inference fast.
* FAQ embeddings are pre-computed when the engine is initialised and cached in
  memory (numpy array), so only the user query is encoded at request time.
* The implementation depends only on the abstract FAQItem schema, so the data
  source can be swapped independently.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from app.models.schemas import FAQItem

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Holds the outcome of a single matching attempt."""

    matched: bool
    faq_id: Optional[str]
    answer: str
    similarity_score: Optional[float]


class FAQMatcher:
    """
    Encodes FAQ questions once at startup and matches user queries at runtime
    using cosine similarity over sentence-transformer embeddings.
    """

    def __init__(
        self,
        model: SentenceTransformer,
        faqs: List[FAQItem],
        similarity_threshold: float,
        fallback_message: str,
    ) -> None:
        self._model = model
        self._faqs = faqs
        self._threshold = similarity_threshold
        self._fallback = fallback_message

        # Pre-compute and normalise embeddings for all FAQ questions.
        self._faq_embeddings: np.ndarray = self._encode_faqs()

    # ── Public interface ──────────────────────────────────────────────────────

    def match(self, user_question: str) -> MatchResult:
        """
        Find the best-matching FAQ for *user_question*.

        Returns a MatchResult with matched=False and the fallback message
        if no FAQ scores above the configured similarity threshold.
        """
        if not self._faqs:
            logger.warning("FAQ list is empty; returning fallback.")
            return MatchResult(
                matched=False,
                faq_id=None,
                answer=self._fallback,
                similarity_score=None,
            )

        # Encode the incoming query (single vector).
        query_embedding = self._encode_query(user_question)

        # Cosine similarity: dot product of normalised vectors equals cosine sim.
        scores: np.ndarray = self._faq_embeddings @ query_embedding  # shape (N,)
        best_idx: int = int(np.argmax(scores))
        best_score: float = float(scores[best_idx])

        logger.debug(
            "Best match: FAQ '%s' with score %.4f (threshold=%.2f).",
            self._faqs[best_idx].id,
            best_score,
            self._threshold,
        )

        if best_score >= self._threshold:
            faq = self._faqs[best_idx]
            return MatchResult(
                matched=True,
                faq_id=faq.id,
                answer=faq.answer,
                similarity_score=round(best_score, 4),
            )

        return MatchResult(
            matched=False,
            faq_id=None,
            answer=self._fallback,
            similarity_score=round(best_score, 4),
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _encode_faqs(self) -> np.ndarray:
        """Encode all FAQ questions into L2-normalised embeddings (N × D)."""
        questions = [faq.question for faq in self._faqs]
        logger.info("Pre-computing embeddings for %d FAQ questions …", len(questions))
        embeddings = self._model.encode(
            questions,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 normalise → dot product = cosine sim
        )
        logger.info("FAQ embeddings ready (shape=%s).", embeddings.shape)
        return embeddings  # type: ignore[return-value]

    def _encode_query(self, text: str) -> np.ndarray:
        """Encode a single user query into an L2-normalised embedding (D,)."""
        return self._model.encode(  # type: ignore[return-value]
            text,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
