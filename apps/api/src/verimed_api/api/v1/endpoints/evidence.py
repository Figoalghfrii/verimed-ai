"""GET /api/v1/evidence/* endpoints for corpus stats and document directory."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from verimed_api.api.deps import SettingsDep, get_ingestion_service
from verimed_api.core.security import sanitize_user_text
from verimed_api.schemas.common import ApiResponse
from verimed_api.schemas.evidence import (
    EvidenceDocumentItem,
    EvidenceDocumentListData,
    EvidenceStatsData,
)
from verimed_api.services.ingestion_service import IngestionService

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get(
    "/stats",
    response_model=ApiResponse[EvidenceStatsData],
    summary="Return indexed evidence corpus counts and active retrieval backends",
)
async def get_evidence_stats(
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_service)],
    settings: SettingsDep,
) -> ApiResponse[EvidenceStatsData]:
    """Report indexed document/chunk counts alongside active embedding & reranker config."""
    stats = await ingestion_service.get_stats()
    return ApiResponse[EvidenceStatsData](
        data=EvidenceStatsData(
            documents_count=stats.documents_count,
            chunks_count=stats.chunks_count,
            synthetic_documents_count=stats.synthetic_documents_count,
            ai_provider=settings.ai_provider,
            embedding_backend=settings.embedding_backend,
            reranker_backend=settings.reranker_backend,
        )
    )


@router.get(
    "/documents",
    response_model=ApiResponse[EvidenceDocumentListData],
    summary="List indexed evidence documents with optional source and text filters",
)
async def list_evidence_documents(
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_service)],
    q: Annotated[str | None, Query(max_length=120)] = None,
    source_type: Annotated[str | None, Query(max_length=64)] = None,
    include_synthetic: bool = True,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ApiResponse[EvidenceDocumentListData]:
    """Browse indexed curated and demonstration evidence documents."""
    sanitized_q = sanitize_user_text(q) if q else None
    sanitized_type = sanitize_user_text(source_type) if source_type else None
    items, total, database_connected = await ingestion_service.list_documents(
        search=sanitized_q,
        source_type=sanitized_type,
        include_synthetic=include_synthetic,
        limit=limit,
        offset=offset,
    )
    return ApiResponse[EvidenceDocumentListData](
        data=EvidenceDocumentListData(
            items=[
                EvidenceDocumentItem(
                    id=item.id,
                    source_name=item.source_name,
                    source_url=item.source_url,
                    title=item.title,
                    authors=item.authors,
                    publication_date=item.publication_date,
                    language_code=item.language_code,
                    source_type=item.source_type,
                    chunks_count=item.chunks_count,
                    is_synthetic_demo=item.is_synthetic_demo,
                    retrieved_at=item.retrieved_at,
                )
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
            database_connected=database_connected,
        )
    )
