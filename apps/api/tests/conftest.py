"""Shared pytest fixtures for VeriMed API tests."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from verimed_api.api.deps import get_health_service
from verimed_api.core.config import Settings
from verimed_api.main import create_app
from verimed_api.schemas.health import DatabaseHealthStatus
from verimed_api.services.health_service import HealthService


class StubHealthRepository:
    """Deterministic stub repository for unit/API tests."""

    def __init__(
        self,
        status: str = "connected",
        pgvector_enabled: bool = True,
        latency_ms: float = 1.25,
    ) -> None:
        self._status = status
        self._pgvector_enabled = pgvector_enabled
        self._latency_ms = latency_ms

    async def check_database(self) -> DatabaseHealthStatus:
        return DatabaseHealthStatus(
            status=self._status,  # type: ignore[arg-type]
            pgvector_enabled=self._pgvector_enabled,
            latency_ms=self._latency_ms,
        )


@pytest.fixture
def test_settings() -> Settings:
    """Return deterministic test Settings."""
    return Settings(
        app_env="test",
        app_name="VeriMed API",
        app_version="0.1.0",
        ai_provider="mock",
    )


@pytest.fixture
async def async_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient wired to the FastAPI app with stubbed health repo."""
    app = create_app()

    def _override_health_service() -> HealthService:
        return HealthService(
            health_repo=StubHealthRepository(),  # type: ignore[arg-type]
            settings=test_settings,
        )

    app.dependency_overrides[get_health_service] = _override_health_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
