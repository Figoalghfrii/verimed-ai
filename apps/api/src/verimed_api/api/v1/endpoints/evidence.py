"""GET /api/v1/evidence/stats endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from verimed_api.api.deps import SettingsDep, get_ingestion_service
from verimed_api.schemas.common import ApiResponse
from verimed_api.schemas.evidence import EvidenceStatsData
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
