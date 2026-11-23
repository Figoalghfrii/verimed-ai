"""Pydantic v2 schemas for evidence items, indexed documents, and citations."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CitationStance = Literal["SUPPORTING", "CONTRADICTING", "CONTEXTUAL"]


class EvidenceSourceItem(BaseModel):
    """Retrieved evidence passage and source provenance returned in verification results."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    citation_key: str = Field(..., examples=["[1]"])
    source_name: str
    source_type: str
    title: str
    source_url: str
    publication_date: date | None = None
    excerpt: str
    stance: CitationStance
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    is_synthetic_demo: bool = True


class EvidenceStatsData(BaseModel):
    """Summary counts of indexed documents and chunks returned by GET /api/v1/evidence/stats."""

    model_config = ConfigDict(extra="forbid")

    documents_count: int = Field(..., ge=0)
    chunks_count: int = Field(..., ge=0)
    synthetic_documents_count: int = Field(..., ge=0)
    ai_provider: str | None = None
    embedding_backend: str | None = None
    reranker_backend: str | None = None


class EvidenceDocumentItem(BaseModel):
    """Metadata summary for a single indexed evidence document."""

    model_config = ConfigDict(extra="forbid")

    id: str
    source_name: str
    source_url: str
    title: str
    authors: str | None = None
    publication_date: date | None = None
    language_code: str
    source_type: str
    chunks_count: int = Field(..., ge=0)
    is_synthetic_demo: bool
    retrieved_at: datetime


class EvidenceDocumentListData(BaseModel):
    """Paginated list of indexed evidence documents returned by GET /api/v1/evidence/documents."""

    model_config = ConfigDict(extra="forbid")

    items: list[EvidenceDocumentItem]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    database_connected: bool
