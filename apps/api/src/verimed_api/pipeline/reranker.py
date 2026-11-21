"""Reranking implementations: lightweight lexical overlap reranker and optional CrossEncoder."""

import math
import re
from dataclasses import replace
from typing import Any

from verimed_api.pipeline.interfaces import RetrievedChunkCandidate

WORD_RE = re.compile(r"\w+", re.UNICODE)
STOPWORDS_ID: frozenset[str] = frozenset(
    {
        "yang",
        "dan",
        "di",
        "ke",
        "dari",
        "untuk",
        "pada",
        "dengan",
        "atau",
        "ini",
        "itu",
        "adalah",
        "dapat",
        "bisa",
        "akan",
        "oleh",
        "juga",
        "tidak",
    }
)


def _content_tokens(text: str) -> set[str]:
    return {
        tok for tok in WORD_RE.findall(text.lower()) if len(tok) > 2 and tok not in STOPWORDS_ID
    }


class LexicalOverlapReranker:
    """Fast deterministic reranker combining hybrid RRF score and meaningful token overlap."""

    async def rerank(
        self,
        claim_text: str,
        candidates: list[RetrievedChunkCandidate],
        min_score: float = 0.35,
    ) -> list[RetrievedChunkCandidate]:
        """Rescore candidates via token overlap + retrieval score and filter by threshold."""
        if not candidates:
            return []

        claim_tokens = _content_tokens(claim_text)
        rescored: list[RetrievedChunkCandidate] = []

        for candidate in candidates:
            chunk_tokens = _content_tokens(f"{candidate.title} {candidate.chunk_text}")
            if claim_tokens and chunk_tokens:
                overlap = len(claim_tokens & chunk_tokens) / len(claim_tokens)
            else:
                overlap = 0.0

            combined = min(
                1.0,
                round(0.45 * candidate.hybrid_score + 0.55 * overlap, 4),
            )
            if combined >= min_score:
                rescored.append(replace(candidate, rerank_score=combined))

        rescored.sort(key=lambda item: item.rerank_score, reverse=True)
        return rescored


class CrossEncoderReranker:
    """Lazy-loaded multilingual CrossEncoder reranker (requires `[ml]` optional extras)."""

    def __init__(self, model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1") -> None:
        self._model_name = model_name
        self._model: Any = None

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as exc:
                raise RuntimeError(
                    "sentence-transformers is not installed. Install optional ML extras with "
                    '`pip install -e ".[ml]"` or set RERANKER_BACKEND=lexical.'
                ) from exc
            self._model = CrossEncoder(self._model_name)
        return self._model

    async def rerank(
        self,
        claim_text: str,
        candidates: list[RetrievedChunkCandidate],
        min_score: float = 0.35,
    ) -> list[RetrievedChunkCandidate]:
        """Score (claim, chunk) pairs via CrossEncoder and normalize logits with sigmoid."""
        if not candidates:
            return []

        model = self._get_model()
        pairs = [(claim_text, candidate.chunk_text) for candidate in candidates]
        raw_scores = model.predict(pairs)

        rescored: list[RetrievedChunkCandidate] = []
        for candidate, raw_logit in zip(candidates, raw_scores, strict=True):
            prob = 1.0 / (1.0 + math.exp(-float(raw_logit)))
            score = round(prob, 4)
            if score >= min_score:
                rescored.append(replace(candidate, rerank_score=score))

        rescored.sort(key=lambda item: item.rerank_score, reverse=True)
        return rescored
