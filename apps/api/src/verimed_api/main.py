"""FastAPI application entrypoint and factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from verimed_api.api.v1.router import api_v1_router
from verimed_api.core.config import Settings, get_settings
from verimed_api.core.exceptions import register_exception_handlers
from verimed_api.core.logging import configure_logging
from verimed_api.core.rate_limit import SlidingWindowRateLimitMiddleware


def create_app(settings_override: Settings | None = None) -> FastAPI:
    """Create and configure the VeriMed FastAPI application."""
    configure_logging()
    settings = settings_override or get_settings()

    expose_docs = settings.should_expose_docs
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "VeriMed — AI-Powered Health Claim Verification and Evidence Intelligence API. "
            "Educational evidence-assistance platform, not a clinical diagnostic tool."
        ),
        openapi_url=f"{settings.api_v1_prefix}/openapi.json" if expose_docs else None,
        docs_url=f"{settings.api_v1_prefix}/docs" if expose_docs else None,
        redoc_url=f"{settings.api_v1_prefix}/redoc" if expose_docs else None,
    )
    if settings_override is not None:
        application.state.settings = settings_override
        application.dependency_overrides[get_settings] = lambda: settings_override

    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    application.add_middleware(
        SlidingWindowRateLimitMiddleware,
        enabled=settings.rate_limit_enabled,
        max_requests=settings.rate_limit_requests_per_minute,
        window_seconds=60,
        exempt_paths={
            f"{settings.api_v1_prefix}/health/live",
        },
        trusted_proxies=settings.trusted_proxies,
        route_limits={
            f"{settings.api_v1_prefix}/verify": settings.verify_rate_limit_requests_per_minute,
            f"{settings.api_v1_prefix}/feedback": settings.feedback_rate_limit_requests_per_minute,
            f"{settings.api_v1_prefix}/client-token": (
                settings.client_token_rate_limit_requests_per_minute
            ),
        },
        max_buckets=settings.rate_limit_max_buckets,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Accept",
            "X-Request-ID",
            "X-API-Key",
            "X-VeriMed-Client-Token",
        ],
    )

    register_exception_handlers(application)
    application.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return application


app = create_app()
