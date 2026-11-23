"""Public anonymous client token endpoint for abuse-resistant browser access."""

import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from verimed_api.core.config import Settings, get_settings
from verimed_api.core.exceptions import AppError
from verimed_api.core.logging import log_security_event
from verimed_api.core.security import issue_signed_token
from verimed_api.schemas.common import ApiResponse, ResponseMeta

router = APIRouter(tags=["Client Access"])


class ClientTokenData(BaseModel):
    """Short-lived anonymous client token payload for public browser sessions."""

    client_token: str
    expires_in_seconds: int
    token_type: str = "Bearer"


@router.post(
    "/client-token",
    response_model=ApiResponse[ClientTokenData],
    summary="Issue short-lived anonymous browser client token",
)
async def issue_client_token(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> ApiResponse[ClientTokenData]:
    """Issue a signed short-lived client token for public browser clients."""
    origin = request.headers.get("origin")
    if (
        settings.should_require_client_auth
        and origin
        and settings.cors_origins
        and "*" not in settings.cors_origins
        and origin not in settings.cors_origins
    ):
        log_security_event(
            "client_token_origin_rejected",
            request_id=getattr(request.state, "request_id", None),
            outcome="blocked",
            details={"origin_present": True},
        )
        raise AppError(
            code="ORIGIN_NOT_ALLOWED",
            message="Origin permintaan tidak diizinkan untuk penerbitan token klien.",
            status_code=403,
        )

    token = issue_signed_token(
        payload={"scope": "public_client", "jti": str(uuid.uuid4())},
        secret=settings.effective_client_auth_secret,
        ttl_seconds=settings.client_token_ttl_seconds,
    )
    return ApiResponse(
        data=ClientTokenData(
            client_token=token,
            expires_in_seconds=settings.client_token_ttl_seconds,
        ),
        meta=ResponseMeta(
            request_id=getattr(request.state, "request_id", str(uuid.uuid4())),
            is_demonstration=(settings.ai_provider == "mock"),
        ),
    )
