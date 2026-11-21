"""Shared pytest fixtures for VeriMed API tests."""

import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from verimed_api.api.deps import (
    get_health_service,
    get_ingestion_service,
    get_verification_service,
)
from verimed_api.core.config import Settings
from verimed_api.main import create_app
from verimed_api.pipeline.citation_validator import ProgrammaticCitationValidator
from verimed_api.pipeline.claim_extractor import DeterministicClaimExtractor
from verimed_api.pipeline.orchestrator import (
    PipelineExecutionOutput,
    VerificationPipelineOrchestrator,
)
from verimed_api.pipeline.providers.embedding_provider import DeterministicHashEmbeddingProvider
from verimed_api.pipeline.providers.mock_provider import MockPipelineProvider
from verimed_api.pipeline.query_normalizer import IndonesianQueryNormalizer
from verimed_api.pipeline.safety_guard import SafetyGuard
from verimed_api.repositories.evidence_repo import EvidenceCorpusStats
from verimed_api.schemas.health import DatabaseHealthStatus
from verimed_api.services.health_service import HealthService
from verimed_api.services.ingestion_service import IngestionService
from verimed_api.services.verification_service import VerificationService


class StubHealthRepository:
    """Deterministic stub repository for health endpoint tests."""

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


class StubVerificationRepository:
    """In-memory stub repository for verification endpoint tests."""

    def __init__(self) -> None:
        self.saved_requests: list[uuid.UUID] = []

    async def save_verification_result(
        self,
        *,
        request_id: uuid.UUID,
        input_text: str,
        language_code: str,
        is_demonstration: bool,
        processing_time_ms: int,
        output: PipelineExecutionOutput,
    ) -> None:
        del input_text, language_code, is_demonstration, processing_time_ms, output
        self.saved_requests.append(request_id)


class StubEvidenceRepository:
    """In-memory stub repository for evidence stats endpoint tests."""

    async def get_corpus_stats(self) -> EvidenceCorpusStats:
        return EvidenceCorpusStats(
            documents_count=5,
            chunks_count=10,
            synthetic_documents_count=5,
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
    """Provide an HTTPX AsyncClient wired to FastAPI with stubbed repositories."""
    app = create_app()

    def _override_health_service() -> HealthService:
        return HealthService(
            health_repo=StubHealthRepository(),  # type: ignore[arg-type]
            settings=test_settings,
        )

    def _override_verification_service() -> VerificationService:
        safety_guard = SafetyGuard()
        mock_provider = MockPipelineProvider(safety_guard=safety_guard)
        orchestrator = VerificationPipelineOrchestrator(
            safety_guard=safety_guard,
            claim_extractor=DeterministicClaimExtractor(),
            query_normalizer=IndonesianQueryNormalizer(),
            retriever=mock_provider,
            reranker=mock_provider,
            assessor=mock_provider,
            explainer=mock_provider,
            citation_validator=ProgrammaticCitationValidator(),
            model_version="mock-0.1.0",
        )
        return VerificationService(
            orchestrator=orchestrator,
            verification_repo=StubVerificationRepository(),  # type: ignore[arg-type]
            settings=test_settings,
        )

    def _override_ingestion_service() -> IngestionService:
        return IngestionService(
            evidence_repo=StubEvidenceRepository(),  # type: ignore[arg-type]
            embedding_provider=DeterministicHashEmbeddingProvider(),
        )

    app.dependency_overrides[get_health_service] = _override_health_service
    app.dependency_overrides[get_verification_service] = _override_verification_service
    app.dependency_overrides[get_ingestion_service] = _override_ingestion_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
