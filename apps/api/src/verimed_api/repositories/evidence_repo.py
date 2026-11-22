"""Repository for curated evidence documents, chunk indexing, and hybrid search."""

import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.models.evidence import EvidenceChunk, EvidenceDocument
from verimed_api.pipeline.fusion import RankedChunkHit

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class ChunkIndexRecord:
    """Chunk text, token count, and embedding vector prepared for persistence."""

    chunk_index: int
    chunk_text: str
    token_count: int
    embedding: list[float]


@dataclass(frozen=True, slots=True)
class EvidenceDocumentRecord:
    """Validated metadata and chunk list for ingesting an evidence document."""

    source_name: str
    source_url: str
    title: str
    authors: str | None
    publication_date: date | None
    retrieved_at: datetime
    language_code: str
    source_type: str
    content_hash: str
    is_synthetic_demo: bool
    chunks: list[ChunkIndexRecord]


@dataclass(frozen=True, slots=True)
class EvidenceCorpusStats:
    """Summary counts of indexed evidence documents and chunks."""

    documents_count: int
    chunks_count: int
    synthetic_documents_count: int


@dataclass(frozen=True, slots=True)
class EvidenceDocumentSummary:
    """Indexed document metadata with chunk count for corpus browsing."""

    id: str
    source_name: str
    source_url: str
    title: str
    authors: str | None
    publication_date: date | None
    language_code: str
    source_type: str
    chunks_count: int
    is_synthetic_demo: bool
    retrieved_at: datetime


def build_safe_or_query(query_text: str, max_terms: int = 16) -> str:
    """Build a safe OR-joined query string for PostgreSQL websearch_to_tsquery."""
    seen: list[str] = []
    for token in TOKEN_RE.findall(query_text.lower()):
        if len(token) >= 2 and token not in seen:
            seen.append(token)
        if len(seen) >= max_terms:
            break
    return " OR ".join(seen)


class EvidenceRepository:
    """Persists and queries curated evidence documents and chunks in PostgreSQL + pgvector."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_document_with_chunks(
        self, record: EvidenceDocumentRecord
    ) -> tuple[uuid.UUID, bool]:
        """Insert document and chunks idempotently by content_hash.

        Returns `(document_id, created_new)`.
        """
        existing_id = await self._session.scalar(
            select(EvidenceDocument.id).where(EvidenceDocument.content_hash == record.content_hash)
        )
        if existing_id is not None:
            return existing_id, False

        doc_id = uuid.uuid4()
        doc_row = EvidenceDocument(
            id=doc_id,
            source_name=record.source_name,
            source_url=record.source_url,
            title=record.title,
            authors=record.authors,
            publication_date=record.publication_date,
            retrieved_at=record.retrieved_at,
            language_code=record.language_code,
            source_type=record.source_type,
            content_hash=record.content_hash,
            content_version=1,
            is_synthetic_demo=record.is_synthetic_demo,
        )
        self._session.add(doc_row)

        for chunk in record.chunks:
            self._session.add(
                EvidenceChunk(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.chunk_text,
                    token_count=chunk.token_count,
                    embedding=chunk.embedding,
                    search_vector=func.to_tsvector("simple", chunk.chunk_text),
                    content_version=1,
                )
            )

        await self._session.commit()
        return doc_id, True

    async def search_lexical(self, query_text: str, limit: int = 20) -> list[RankedChunkHit]:
        """Run PostgreSQL full-text search using websearch_to_tsquery('simple', ...)."""
        or_query = build_safe_or_query(query_text)
        if not or_query:
            return []

        ts_query = func.websearch_to_tsquery("simple", or_query)
        rank_expr = func.ts_rank_cd(EvidenceChunk.search_vector, ts_query)

        stmt = (
            select(
                EvidenceChunk.id,
                EvidenceDocument.source_name,
                EvidenceDocument.source_type,
                EvidenceDocument.title,
                EvidenceDocument.source_url,
                EvidenceDocument.publication_date,
                EvidenceChunk.chunk_text,
                rank_expr.label("lexical_rank"),
                EvidenceDocument.is_synthetic_demo,
            )
            .join(EvidenceDocument, EvidenceChunk.document_id == EvidenceDocument.id)
            .where(EvidenceChunk.search_vector.op("@@")(ts_query))
            .order_by(rank_expr.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            RankedChunkHit(
                chunk_id=str(row.id),
                source_name=row.source_name,
                source_type=row.source_type,
                title=row.title,
                source_url=row.source_url,
                publication_date=row.publication_date,
                chunk_text=row.chunk_text,
                raw_score=min(1.0, float(row.lexical_rank or 0.0)),
                is_synthetic_demo=bool(row.is_synthetic_demo),
            )
            for row in rows
        ]

    async def search_vector(
        self, query_embedding: list[float], limit: int = 20
    ) -> list[RankedChunkHit]:
        """Run pgvector cosine similarity search over indexed chunk embeddings."""
        if not query_embedding:
            return []

        distance_expr = EvidenceChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(
                EvidenceChunk.id,
                EvidenceDocument.source_name,
                EvidenceDocument.source_type,
                EvidenceDocument.title,
                EvidenceDocument.source_url,
                EvidenceDocument.publication_date,
                EvidenceChunk.chunk_text,
                distance_expr.label("cosine_distance"),
                EvidenceDocument.is_synthetic_demo,
            )
            .join(EvidenceDocument, EvidenceChunk.document_id == EvidenceDocument.id)
            .where(EvidenceChunk.embedding.is_not(None))
            .order_by(distance_expr.asc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            RankedChunkHit(
                chunk_id=str(row.id),
                source_name=row.source_name,
                source_type=row.source_type,
                title=row.title,
                source_url=row.source_url,
                publication_date=row.publication_date,
                chunk_text=row.chunk_text,
                raw_score=max(0.0, min(1.0, 1.0 - float(row.cosine_distance or 1.0))),
                is_synthetic_demo=bool(row.is_synthetic_demo),
            )
            for row in rows
        ]

    async def get_corpus_stats(self) -> EvidenceCorpusStats:
        """Return total counts of indexed evidence documents and chunks."""
        docs_count = await self._session.scalar(select(func.count(EvidenceDocument.id))) or 0
        chunks_count = await self._session.scalar(select(func.count(EvidenceChunk.id))) or 0
        synth_count = (
            await self._session.scalar(
                select(func.count(EvidenceDocument.id)).where(
                    EvidenceDocument.is_synthetic_demo.is_(True)
                )
            )
            or 0
        )
        return EvidenceCorpusStats(
            documents_count=int(docs_count),
            chunks_count=int(chunks_count),
            synthetic_documents_count=int(synth_count),
        )

    async def list_documents(
        self,
        *,
        search: str | None = None,
        source_type: str | None = None,
        include_synthetic: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EvidenceDocumentSummary], int]:
        """Return paginated evidence documents matching optional filters."""
        filters = []
        if not include_synthetic:
            filters.append(EvidenceDocument.is_synthetic_demo.is_(False))
        if source_type:
            filters.append(EvidenceDocument.source_type == source_type)
        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(
                    EvidenceDocument.title.ilike(pattern),
                    EvidenceDocument.source_name.ilike(pattern),
                )
            )

        count_stmt = select(func.count(EvidenceDocument.id))
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int(await self._session.scalar(count_stmt) or 0)

        stmt = (
            select(
                EvidenceDocument.id,
                EvidenceDocument.source_name,
                EvidenceDocument.source_url,
                EvidenceDocument.title,
                EvidenceDocument.authors,
                EvidenceDocument.publication_date,
                EvidenceDocument.language_code,
                EvidenceDocument.source_type,
                EvidenceDocument.is_synthetic_demo,
                EvidenceDocument.retrieved_at,
                func.count(EvidenceChunk.id).label("chunks_count"),
            )
            .outerjoin(EvidenceChunk, EvidenceChunk.document_id == EvidenceDocument.id)
            .group_by(EvidenceDocument.id)
            .order_by(
                EvidenceDocument.is_synthetic_demo.asc(),
                EvidenceDocument.retrieved_at.desc(),
                EvidenceDocument.title.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        if filters:
            stmt = stmt.where(*filters)

        rows = (await self._session.execute(stmt)).all()
        items = [
            EvidenceDocumentSummary(
                id=str(row.id),
                source_name=row.source_name,
                source_url=row.source_url,
                title=row.title,
                authors=row.authors,
                publication_date=row.publication_date,
                language_code=row.language_code,
                source_type=row.source_type,
                chunks_count=int(row.chunks_count or 0),
                is_synthetic_demo=bool(row.is_synthetic_demo),
                retrieved_at=row.retrieved_at,
            )
            for row in rows
        ]
        return items, total
