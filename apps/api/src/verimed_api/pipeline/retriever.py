"""Hybrid lexical + pgvector evidence retriever using Reciprocal Rank Fusion (RRF)."""

from typing import Protocol

from verimed_api.pipeline.fusion import RankedChunkHit, fuse_ranked_lists
from verimed_api.pipeline.interfaces import RetrievedChunkCandidate
from verimed_api.pipeline.providers.embedding_provider import EmbeddingProviderProtocol


class EvidenceSearchRepositoryProtocol(Protocol):
    """Subset of EvidenceRepository methods required by HybridPgVectorRetriever."""

    async def search_lexical(self, query_text: str, limit: int = 20) -> list[RankedChunkHit]: ...

    async def search_vector(
        self, query_embedding: list[float], limit: int = 20
    ) -> list[RankedChunkHit]: ...


class HybridPgVectorRetriever:
    """Combines PostgreSQL full-text search and pgvector cosine search via RRF."""

    def __init__(
        self,
        evidence_repo: EvidenceSearchRepositoryProtocol,
        embedding_provider: EmbeddingProviderProtocol,
        *,
        candidate_pool_size: int = 20,
        rrf_k: int = 60,
    ) -> None:
        self._evidence_repo = evidence_repo
        self._embedding_provider = embedding_provider
        self._candidate_pool_size = candidate_pool_size
        self._rrf_k = rrf_k

    async def retrieve(
        self,
        claim_text: str,
        normalized_query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunkCandidate]:
        """Run lexical + semantic retrieval and merge with Reciprocal Rank Fusion."""
        query_embedding = await self._embedding_provider.embed_query(claim_text)

        lexical_hits = await self._evidence_repo.search_lexical(
            normalized_query, limit=self._candidate_pool_size
        )
        vector_hits = await self._evidence_repo.search_vector(
            query_embedding, limit=self._candidate_pool_size
        )

        fused = fuse_ranked_lists(
            lexical_hits,
            vector_hits,
            rrf_k=self._rrf_k,
            top_k=top_k,
        )

        return [
            RetrievedChunkCandidate(
                chunk_id=hit.chunk_id,
                source_name=hit.source_name,
                source_type=hit.source_type,
                title=hit.title,
                source_url=hit.source_url,
                publication_date=hit.publication_date,
                chunk_text=hit.chunk_text,
                lexical_score=hit.lexical_score,
                vector_score=hit.vector_score,
                hybrid_score=hit.hybrid_score,
                rerank_score=hit.hybrid_score,
                stance="CONTEXTUAL",
                is_synthetic_demo=hit.is_synthetic_demo,
            )
            for hit in fused
        ]
