"""POST /api/v1/verify endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from verimed_api.api.deps import get_verification_service, verify_client_credential
from verimed_api.schemas.common import ApiResponse
from verimed_api.schemas.verification import (
    VerificationRequestInput,
    VerificationResponseData,
)
from verimed_api.services.verification_service import VerificationService

router = APIRouter(tags=["verification"])


@router.post(
    "/verify",
    response_model=ApiResponse[VerificationResponseData],
    summary="Verify a health-related claim against curated/demonstration evidence",
)
async def verify_health_claim(
    payload: VerificationRequestInput,
    verification_service: Annotated[VerificationService, Depends(get_verification_service)],
    _client: Annotated[None, Depends(verify_client_credential)],
) -> ApiResponse[VerificationResponseData]:
    """Validate and evaluate a health claim through the VeriMed verification pipeline."""
    data = await verification_service.verify_claim(payload)
    return ApiResponse[VerificationResponseData](data=data)
