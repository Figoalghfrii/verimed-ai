"""Evidence documents, chunks (with pgvector), retrieval results, and citations."""

import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from verimed_api.models.base import Base, TimestampUUIDMixin


class EvidenceDocument(TimestampUUIDMixin, Base):
    """Curated authoritative medical document metadata."""

    __tablename__ = "evidence_documents"

    source_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), default="id", nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    content_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_synthetic_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    chunks: Mapped[list["EvidenceChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class EvidenceChunk(TimestampUUIDMixin, Base):
    """Indexed passage chunk with 768-d semantic vector and full-text search vector."""

    __tablename__ = "evidence_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence_documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
    content_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    document: Mapped["EvidenceDocument"] = relationship(back_populates="chunks")


class RetrievalResult(TimestampUUIDMixin, Base):
    """Audit trail of candidate chunks retrieved and reranked for an extracted claim."""

    __tablename__ = "retrieval_results"

    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("extracted_claims.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence_chunks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lexical_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    vector_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hybrid_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rerank_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Citation(TimestampUUIDMixin, Base):
    """Explicit grounding link between a claim assessment and an evidence chunk."""

    __tablename__ = "citations"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("claim_assessments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence_chunks.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    citation_key: Mapped[str] = mapped_column(String(16), nullable=False)
    stance: Mapped[str] = mapped_column(String(32), nullable=False)
    quoted_span: Mapped[str | None] = mapped_column(Text, nullable=True)
