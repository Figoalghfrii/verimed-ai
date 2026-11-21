"""Reciprocal Rank Fusion (RRF) for combining lexical and dense vector retrieval results."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class RankedChunkHit:
    """Single ranked hit from either lexical or semantic vector search."""

    chunk_id: str
    source_name: str
    source_type: str
    title: str
    source_url: str
    publication_date: date | None
    chunk_text: str
    raw_score: float
    is_synthetic_demo: bool


@dataclass(frozen=True, slots=True)
class FusedChunkHit:
    """Combined candidate produced by Reciprocal Rank Fusion."""

    chunk_id: str
    source_name: str
    source_type: str
    title: str
    source_url: str
    publication_date: date | None
    chunk_text: str
    lexical_score: float
    vector_score: float
    hybrid_score: float
    is_synthetic_demo: bool


def fuse_ranked_lists(
    lexical_hits: list[RankedChunkHit],
    vector_hits: list[RankedChunkHit],
    *,
    rrf_k: int = 60,
    top_k: int = 10,
) -> list[FusedChunkHit]:
    """Merge lexical and vector ranked hits via Reciprocal Rank Fusion (RRF).

    Scores are normalized to [0.0, 1.0] relative to `2 / (rrf_k + 1)` so downstream
    threshold gates remain consistent across queries.
    """
    if not lexical_hits and not vector_hits:
        return []

    max_theoretical = 2.0 / (rrf_k + 1)
    by_id: dict[str, RankedChunkHit] = {}
    lexical_scores: dict[str, float] = {}
    vector_scores: dict[str, float] = {}
    rrf_totals: dict[str, float] = {}

    for rank, hit in enumerate(lexical_hits, start=1):
        by_id[hit.chunk_id] = hit
        lexical_scores[hit.chunk_id] = max(0.0, min(1.0, hit.raw_score))
        rrf_totals[hit.chunk_id] = rrf_totals.get(hit.chunk_id, 0.0) + 1.0 / (rrf_k + rank)

    for rank, hit in enumerate(vector_hits, start=1):
        by_id.setdefault(hit.chunk_id, hit)
        vector_scores[hit.chunk_id] = max(0.0, min(1.0, hit.raw_score))
        rrf_totals[hit.chunk_id] = rrf_totals.get(hit.chunk_id, 0.0) + 1.0 / (rrf_k + rank)

    fused: list[FusedChunkHit] = []
    for chunk_id, raw_rrf in rrf_totals.items():
        base = by_id[chunk_id]
        normalized_hybrid = min(1.0, raw_rrf / max_theoretical)
        fused.append(
            FusedChunkHit(
                chunk_id=chunk_id,
                source_name=base.source_name,
                source_type=base.source_type,
                title=base.title,
                source_url=base.source_url,
                publication_date=base.publication_date,
                chunk_text=base.chunk_text,
                lexical_score=round(lexical_scores.get(chunk_id, 0.0), 4),
                vector_score=round(vector_scores.get(chunk_id, 0.0), 4),
                hybrid_score=round(normalized_hybrid, 4),
                is_synthetic_demo=base.is_synthetic_demo,
            )
        )

    fused.sort(key=lambda item: item.hybrid_score, reverse=True)
    return fused[:top_k]
