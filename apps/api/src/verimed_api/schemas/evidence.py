"""Pydantic v2 schemas for evidence items and citations."""

from datetime import date
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
    ai_provider: str
    embedding_backend: str
    reranker_backend: str
