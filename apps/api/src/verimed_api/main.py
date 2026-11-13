"""FastAPI application entrypoint and factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from verimed_api.api.v1.router import api_v1_router
from verimed_api.core.config import get_settings
from verimed_api.core.exceptions import register_exception_handlers
from verimed_api.core.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the VeriMed FastAPI application."""
    configure_logging()
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "VeriMed — AI-Powered Health Claim Verification and Evidence Intelligence API. "
            "Educational evidence-assistance platform, not a clinical diagnostic tool."
        ),
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "X-Request-ID"],
    )

    register_exception_handlers(application)
    application.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return application


app = create_app()
