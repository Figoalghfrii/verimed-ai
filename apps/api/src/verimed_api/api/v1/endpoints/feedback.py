"""POST /api/v1/feedback and GET /api/v1/feedback/stats endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from verimed_api.api.deps import get_feedback_service
from verimed_api.schemas.common import ApiResponse
from verimed_api.schemas.feedback import (
    FeedbackRequestInput,
    FeedbackResponseData,
    FeedbackStatsData,
)
from verimed_api.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[FeedbackResponseData],
    summary="Submit anonymous user feedback on explanation clarity",
)
async def submit_feedback(
    payload: FeedbackRequestInput,
    feedback_service: Annotated[FeedbackService, Depends(get_feedback_service)],
) -> ApiResponse[FeedbackResponseData]:
    """Store anonymous user clarity feedback for a completed verification."""
    data = await feedback_service.submit_feedback(payload)
    return ApiResponse[FeedbackResponseData](data=data)


@router.get(
    "/stats",
    response_model=ApiResponse[FeedbackStatsData],
    summary="Return aggregated anonymous explanation clarity feedback statistics",
)
async def get_feedback_stats(
    feedback_service: Annotated[FeedbackService, Depends(get_feedback_service)],
) -> ApiResponse[FeedbackStatsData]:
    """Return aggregated anonymous feedback metrics without exposing user comments."""
    data = await feedback_service.get_stats()
    return ApiResponse[FeedbackStatsData](data=data)
