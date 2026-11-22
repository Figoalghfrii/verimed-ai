"""Shared pytest fixtures for VeriMed API tests."""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from verimed_api.api.deps import (
    get_feedback_service,
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
from verimed_api.repositories.evidence_repo import (
    EvidenceCorpusStats,
    EvidenceDocumentSummary,
)
from verimed_api.repositories.feedback_repo import FeedbackStatsSummary
from verimed_api.schemas.health import DatabaseHealthStatus
from verimed_api.services.feedback_service import FeedbackService
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
    """In-memory stub repository for evidence stats and documents endpoint tests."""

    def __init__(self) -> None:
        now = datetime(2026, 11, 22, 5, 0, tzinfo=UTC)
        self._documents = [
            EvidenceDocumentSummary(
                id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                source_name="Kementerian Kesehatan RI",
                source_url="https://kemkes.go.id/id/cuci-tangan-pakai-sabun-perilaku-sederhana-berdampak-luar-biasa",
                title="Cuci Tangan Pakai Sabun, Perilaku Sederhana Berdampak Luar Biasa",
                authors="Kementerian Kesehatan Republik Indonesia",
                publication_date=None,
                language_code="id",
                source_type="OFFICIAL_GUIDELINE",
                chunks_count=2,
                is_synthetic_demo=False,
                retrieved_at=now,
            ),
            EvidenceDocumentSummary(
                id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                source_name="VeriMed Demo Corpus — Kebersihan Tangan",
                source_url="https://demo.verimed.local/synthetic/ctps-infeksi",
                title="[Contoh Simulasi] Efektivitas Cuci Tangan Pakai Sabun",
                authors="VeriMed Synthetic Demo Corpus",
                publication_date=None,
                language_code="id",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                chunks_count=2,
                is_synthetic_demo=True,
                retrieved_at=now,
            ),
        ]

    async def get_corpus_stats(self) -> EvidenceCorpusStats:
        return EvidenceCorpusStats(
            documents_count=5,
            chunks_count=10,
            synthetic_documents_count=5,
        )

    async def list_documents(
        self,
        *,
        search: str | None = None,
        source_type: str | None = None,
        include_synthetic: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EvidenceDocumentSummary], int]:
        filtered = list(self._documents)
        if not include_synthetic:
            filtered = [doc for doc in filtered if not doc.is_synthetic_demo]
        if source_type:
            filtered = [doc for doc in filtered if doc.source_type == source_type]
        if search:
            needle = search.lower()
            filtered = [
                doc
                for doc in filtered
                if needle in doc.title.lower() or needle in doc.source_name.lower()
            ]
        return filtered[offset : offset + limit], len(filtered)


class StubFeedbackRepository:
    """In-memory stub repository for user feedback endpoint tests."""

    def __init__(self, known_requests: list[uuid.UUID]) -> None:
        self._known_requests = known_requests
        self.saved_feedback: list[dict[str, object]] = []

    async def request_exists(self, request_id: uuid.UUID) -> bool:
        return request_id in self._known_requests

    async def assessment_belongs_to_request(
        self,
        assessment_id: uuid.UUID,
        request_id: uuid.UUID,
    ) -> bool:
        del assessment_id
        return request_id in self._known_requests

    async def create_feedback(
        self,
        *,
        feedback_id: uuid.UUID,
        request_id: uuid.UUID,
        assessment_id: uuid.UUID | None,
        is_helpful: bool,
        feedback_category: str | None,
        comment_sanitized: str | None,
    ) -> None:
        self.saved_feedback.append(
            {
                "feedback_id": feedback_id,
                "request_id": request_id,
                "assessment_id": assessment_id,
                "is_helpful": is_helpful,
                "feedback_category": feedback_category,
                "comment_sanitized": comment_sanitized,
            }
        )

    async def get_stats(self) -> FeedbackStatsSummary:
        total = len(self.saved_feedback)
        helpful = sum(1 for item in self.saved_feedback if item["is_helpful"] is True)
        by_category: dict[str, int] = {}
        for item in self.saved_feedback:
            cat = item.get("feedback_category")
            if isinstance(cat, str) and cat:
                by_category[cat] = by_category.get(cat, 0) + 1
        return FeedbackStatsSummary(
            total_count=total,
            helpful_count=helpful,
            not_helpful_count=total - helpful,
            by_category=by_category,
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
    verification_repo = StubVerificationRepository()
    feedback_repo = StubFeedbackRepository(known_requests=verification_repo.saved_requests)

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
            verification_repo=verification_repo,  # type: ignore[arg-type]
            settings=test_settings,
        )

    def _override_ingestion_service() -> IngestionService:
        return IngestionService(
            evidence_repo=StubEvidenceRepository(),  # type: ignore[arg-type]
            embedding_provider=DeterministicHashEmbeddingProvider(),
        )

    def _override_feedback_service() -> FeedbackService:
        return FeedbackService(feedback_repo=feedback_repo)  # type: ignore[arg-type]

    app.dependency_overrides[get_health_service] = _override_health_service
    app.dependency_overrides[get_verification_service] = _override_verification_service
    app.dependency_overrides[get_ingestion_service] = _override_ingestion_service
    app.dependency_overrides[get_feedback_service] = _override_feedback_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
