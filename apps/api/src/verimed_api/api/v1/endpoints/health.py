"""GET /api/v1/health endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from verimed_api.api.deps import get_health_service
from verimed_api.schemas.common import ApiResponse
from verimed_api.schemas.health import HealthCheckData, LivenessData
from verimed_api.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get(
    "/health/live",
    response_model=ApiResponse[LivenessData],
    summary="Minimal liveness probe without database or operational metadata",
)
async def check_liveness() -> ApiResponse[LivenessData]:
    """Return unprivileged liveness indicator for container probes."""
    return ApiResponse[LivenessData](data=LivenessData())


@router.get(
    "/health",
    response_model=ApiResponse[HealthCheckData],
    summary="Check API and PostgreSQL + pgvector health",
)
async def check_health(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ApiResponse[HealthCheckData]:
    """Return operational status of the API and PostgreSQL/pgvector database."""
    data = await health_service.get_health_status()
    return ApiResponse[HealthCheckData](data=data)
