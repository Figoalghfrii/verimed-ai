"""Integration tests for SlidingWindowRateLimitMiddleware."""

from httpx import ASGITransport, AsyncClient

from verimed_api.api.deps import get_health_service, get_ingestion_service
from verimed_api.core.config import Settings
from verimed_api.main import create_app
from verimed_api.pipeline.providers.embedding_provider import (
    DeterministicHashEmbeddingProvider,
)
from verimed_api.repositories.evidence_repo import EvidenceCorpusStats
from verimed_api.schemas.health import DatabaseHealthStatus
from verimed_api.services.health_service import HealthService
from verimed_api.services.ingestion_service import IngestionService


class _LocalHealthRepo:
    async def check_database(self) -> DatabaseHealthStatus:
        return DatabaseHealthStatus(status="connected", pgvector_enabled=True, latency_ms=1.0)


class _LocalEvidenceRepo:
    async def get_corpus_stats(self) -> EvidenceCorpusStats:
        return EvidenceCorpusStats(documents_count=5, chunks_count=10, synthetic_documents_count=5)


async def test_rate_limit_middleware_enforces_limit_and_exempts_health() -> None:
    """Requests exceeding per-minute limit receive 429 ErrorResponse while /health stays exempt."""
    limited_settings = Settings(
        app_env="test",
        rate_limit_enabled=True,
        rate_limit_requests_per_minute=2,
    )
    app = create_app(settings_override=limited_settings)

    app.dependency_overrides[get_health_service] = lambda: HealthService(
        health_repo=_LocalHealthRepo(),  # type: ignore[arg-type]
        settings=limited_settings,
    )
    app.dependency_overrides[get_ingestion_service] = lambda: IngestionService(
        evidence_repo=_LocalEvidenceRepo(),  # type: ignore[arg-type]
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res1 = await client.get("/api/v1/evidence/stats")
        assert res1.status_code == 200
        assert res1.headers["X-RateLimit-Limit"] == "2"
        assert res1.headers["X-RateLimit-Remaining"] == "1"

        res2 = await client.get("/api/v1/evidence/stats")
        assert res2.status_code == 200
        assert res2.headers["X-RateLimit-Remaining"] == "0"

        res3 = await client.get("/api/v1/evidence/stats")
        assert res3.status_code == 429
        assert res3.headers["Retry-After"]
        payload = res3.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == "RATE_LIMIT_EXCEEDED"

        # Health endpoint must remain exempt even after limit is reached
        health_res = await client.get("/api/v1/health")
        assert health_res.status_code == 200
