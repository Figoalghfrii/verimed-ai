"""Service for validating, chunking, embedding, and indexing curated evidence documents."""

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime

from verimed_api.core.security import is_safe_external_url
from verimed_api.pipeline.chunker import DocumentChunker, compute_content_hash
from verimed_api.pipeline.providers.embedding_provider import EmbeddingProviderProtocol
from verimed_api.repositories.evidence_repo import (
    ChunkIndexRecord,
    EvidenceCorpusStats,
    EvidenceDocumentRecord,
    EvidenceRepository,
)


@dataclass(frozen=True, slots=True)
class IngestionDocumentInput:
    """Validated input document passed to IngestionService."""

    source_name: str
    source_url: str
    title: str
    body_text: str
    source_type: str
    language_code: str = "id"
    authors: str | None = None
    publication_date: date | None = None
    is_synthetic_demo: bool = False


class IngestionService:
    """Chunks, embeds, and persists curated public-health documents into PostgreSQL + pgvector."""

    def __init__(
        self,
        evidence_repo: EvidenceRepository,
        embedding_provider: EmbeddingProviderProtocol,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self._evidence_repo = evidence_repo
        self._embedding_provider = embedding_provider
        self._chunker = chunker or DocumentChunker()

    async def ingest_document(self, item: IngestionDocumentInput) -> tuple[uuid.UUID, bool]:
        """Validate source provenance, chunk text, generate embeddings, and upsert into DB."""
        if not item.is_synthetic_demo and not is_safe_external_url(item.source_url):
            raise ValueError(
                f"Unsafe or non-HTTPS source URL rejected by SSRF guard: {item.source_url}"
            )

        chunks = self._chunker.chunk_text(item.body_text)
        if not chunks:
            raise ValueError("Document body_text produced zero valid chunks")

        vectors = await self._embedding_provider.embed_documents([c.chunk_text for c in chunks])

        chunk_records = [
            ChunkIndexRecord(
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                token_count=chunk.token_count,
                embedding=vector,
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

        record = EvidenceDocumentRecord(
            source_name=item.source_name,
            source_url=item.source_url,
            title=item.title,
            authors=item.authors,
            publication_date=item.publication_date,
            retrieved_at=datetime.now(UTC),
            language_code=item.language_code,
            source_type=item.source_type,
            content_hash=compute_content_hash(f"{item.title}\n{item.body_text}"),
            is_synthetic_demo=item.is_synthetic_demo,
            chunks=chunk_records,
        )
        return await self._evidence_repo.upsert_document_with_chunks(record)

    async def get_stats(self) -> EvidenceCorpusStats:
        """Return indexed evidence document and chunk counts."""
        return await self._evidence_repo.get_corpus_stats()
