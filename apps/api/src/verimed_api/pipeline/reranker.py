"""Reranking implementations: lightweight lexical overlap reranker and optional CrossEncoder."""

import asyncio
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
STOPWORDS_EN: frozenset[str] = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "are",
        "was",
        "were",
        "can",
        "could",
        "will",
        "would",
        "not",
        "does",
        "did",
        "has",
        "have",
        "had",
        "all",
        "into",
        "about",
        "use",
        "using",
    }
)
STOPWORDS: frozenset[str] = STOPWORDS_ID | STOPWORDS_EN

BILINGUAL_TOKEN_ALIASES: dict[str, frozenset[str]] = {
    "washing": frozenset({"cuci", "mencuci"}),
    "wash": frozenset({"cuci", "mencuci"}),
    "handwashing": frozenset({"cuci", "mencuci", "tangan"}),
    "hands": frozenset({"tangan"}),
    "hand": frozenset({"tangan"}),
    "soap": frozenset({"sabun"}),
    "running": frozenset({"mengalir"}),
    "water": frozenset({"air"}),
    "prevents": frozenset({"mencegah", "pencegahan"}),
    "prevent": frozenset({"mencegah", "pencegahan"}),
    "reduces": frozenset({"menurunkan", "mengurangi"}),
    "reduce": frozenset({"menurunkan", "mengurangi"}),
    "risk": frozenset({"risiko"}),
    "diarrhea": frozenset({"diare"}),
    "respiratory": frozenset({"pernapasan"}),
    "infections": frozenset({"infeksi"}),
    "infection": frozenset({"infeksi"}),
    "antibiotic": frozenset({"antibiotik"}),
    "antibiotics": frozenset({"antibiotik"}),
    "virus": frozenset({"virus"}),
    "viral": frozenset({"virus"}),
    "flu": frozenset({"flu", "influenza"}),
    "cold": frozenset({"pilek"}),
    "soursop": frozenset({"sirsak"}),
    "cancer": frozenset({"kanker"}),
    "chemotherapy": frozenset({"kemoterapi"}),
    "cure": frozenset({"menyembuhkan", "penyembuh"}),
    "cures": frozenset({"menyembuhkan"}),
    "herbal": frozenset({"herbal", "jamu", "tradisional"}),
    "vaccine": frozenset({"vaksin", "vaksinasi", "imunisasi"}),
    "vaccines": frozenset({"vaksin", "vaksinasi", "imunisasi"}),
    "vaccination": frozenset({"vaksinasi", "vaksin", "imunisasi"}),
    "immunization": frozenset({"imunisasi", "vaksinasi"}),
    "measles": frozenset({"campak"}),
    "sugar": frozenset({"gula", "glukosa"}),
    "salt": frozenset({"garam", "natrium"}),
    "fat": frozenset({"lemak"}),
    "hypertension": frozenset({"hipertensi", "tekanan", "darah"}),
    "dengue": frozenset({"dengue", "dbd"}),
    "breastfeeding": frozenset({"asi", "menyusui"}),
    "stunting": frozenset({"stunting"}),
    "cervical": frozenset({"serviks"}),
}


def _content_tokens(text: str) -> set[str]:
    return {tok for tok in WORD_RE.findall(text.lower()) if len(tok) > 2 and tok not in STOPWORDS}


class LexicalOverlapReranker:
    """Fast deterministic reranker combining hybrid RRF score and meaningful token overlap."""

    async def rerank(
        self,
        claim_text: str,
        candidates: list[RetrievedChunkCandidate],
        min_score: float = 0.35,
    ) -> list[RetrievedChunkCandidate]:
        """Rescore candidates via bilingual-aware token overlap + retrieval score."""
        if not candidates:
            return []

        claim_tokens = _content_tokens(claim_text)
        rescored: list[RetrievedChunkCandidate] = []

        for candidate in candidates:
            chunk_tokens = _content_tokens(f"{candidate.title} {candidate.chunk_text}")
            if claim_tokens and chunk_tokens:
                matched_count = sum(
                    1
                    for tok in claim_tokens
                    if tok in chunk_tokens
                    or bool(BILINGUAL_TOKEN_ALIASES.get(tok, frozenset()) & chunk_tokens)
                )
                overlap = matched_count / len(claim_tokens)
            else:
                overlap = 0.0

            if overlap < 0.25:
                continue

            combined = min(
                1.0,
                round(0.25 * candidate.hybrid_score + 0.75 * overlap, 4),
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
        raw_scores = await asyncio.to_thread(model.predict, pairs)

        rescored: list[RetrievedChunkCandidate] = []
        for candidate, raw_logit in zip(candidates, raw_scores, strict=True):
            prob = 1.0 / (1.0 + math.exp(-float(raw_logit)))
            score = round(prob, 4)
            if score >= min_score:
                rescored.append(replace(candidate, rerank_score=score))

        rescored.sort(key=lambda item: item.rerank_score, reverse=True)
        return rescored
