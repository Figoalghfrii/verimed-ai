"""FastAPI dependency injection providers."""

import hmac
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.core.config import Settings, get_settings
from verimed_api.core.database import get_db_session
from verimed_api.core.exceptions import AppError
from verimed_api.core.logging import log_security_event
from verimed_api.core.security import verify_signed_token
from verimed_api.pipeline.citation_validator import ProgrammaticCitationValidator
from verimed_api.pipeline.claim_extractor import DeterministicClaimExtractor
from verimed_api.pipeline.interfaces import (
    EvidenceAssessorProtocol,
    EvidenceRerankerProtocol,
    EvidenceRetrieverProtocol,
    GroundedExplainerProtocol,
)
from verimed_api.pipeline.orchestrator import VerificationPipelineOrchestrator
from verimed_api.pipeline.providers.configurable_provider import (
    ConfigurableLLMAssessorExplainer,
)
from verimed_api.pipeline.providers.embedding_provider import (
    DeterministicHashEmbeddingProvider,
    EmbeddingProviderProtocol,
    SentenceTransformerEmbeddingProvider,
)
from verimed_api.pipeline.providers.hybrid_grounded_provider import (
    HybridGroundedAssessor,
    HybridGroundedExplainer,
)
from verimed_api.pipeline.providers.mock_provider import MockPipelineProvider
from verimed_api.pipeline.query_normalizer import IndonesianQueryNormalizer
from verimed_api.pipeline.reranker import CrossEncoderReranker, LexicalOverlapReranker
from verimed_api.pipeline.retriever import HybridPgVectorRetriever
from verimed_api.pipeline.safety_guard import SafetyGuard
from verimed_api.repositories.evidence_repo import EvidenceRepository
from verimed_api.repositories.feedback_repo import FeedbackRepository
from verimed_api.repositories.health_repo import HealthRepository
from verimed_api.repositories.verification_repo import VerificationRepository
from verimed_api.services.feedback_service import FeedbackService
from verimed_api.services.health_service import HealthService
from verimed_api.services.ingestion_service import IngestionService
from verimed_api.services.verification_service import VerificationService

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@lru_cache
def _cached_embedding_provider(
    backend: str, dimension: int, model_name: str
) -> EmbeddingProviderProtocol:
    if backend == "sentence_transformers":
        return SentenceTransformerEmbeddingProvider(model_name=model_name)
    return DeterministicHashEmbeddingProvider(dimension=dimension)


@lru_cache
def _cached_reranker(backend: str, model_name: str) -> EvidenceRerankerProtocol:
    if backend == "cross_encoder":
        return CrossEncoderReranker(model_name=model_name)
    return LexicalOverlapReranker()


def get_embedding_provider(settings: SettingsDep) -> EmbeddingProviderProtocol:
    """Return configured embedding provider instance."""
    return _cached_embedding_provider(
        settings.embedding_backend,
        settings.embedding_dimension,
        settings.embedding_model_name,
    )


def get_health_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> HealthService:
    """Provide configured HealthService instance."""
    repo = HealthRepository(session=session)
    return HealthService(health_repo=repo, settings=settings)


def get_ingestion_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> IngestionService:
    """Provide configured IngestionService for curated document indexing."""
    evidence_repo = EvidenceRepository(session=session)
    embedding_provider = get_embedding_provider(settings=settings)
    return IngestionService(
        evidence_repo=evidence_repo,
        embedding_provider=embedding_provider,
    )


def verify_client_credential(
    request: Request,
    settings: SettingsDep,
) -> None:
    """Enforce API key or signed anonymous client token when client auth is required."""
    if not settings.should_require_client_auth:
        return

    api_key = request.headers.get("x-api-key")
    if api_key and settings.client_api_keys:
        if any(
            hmac.compare_digest(api_key, configured_key)
            for configured_key in settings.client_api_keys
            if configured_key
        ):
            return

    client_token = request.headers.get("x-verimed-client-token")
    if client_token:
        claims = verify_signed_token(
            client_token,
            secret=settings.effective_client_auth_secret,
        )
        if claims and claims.get("scope") == "public_client":
            return

    log_security_event(
        "client_auth_rejected",
        request_id=getattr(request.state, "request_id", None),
        client_ip=request.client.host if request.client else None,
        outcome="blocked",
        details={"path": request.url.path},
    )
    raise AppError(
        code="CLIENT_AUTH_REQUIRED",
        message="Kredensial klien diperlukan untuk mengakses layanan ini.",
        status_code=401,
    )


def get_feedback_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> FeedbackService:
    """Provide configured FeedbackService instance."""
    repo = FeedbackRepository(session=session)
    return FeedbackService(feedback_repo=repo, settings=settings)


def get_verification_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> VerificationService:
    """Provide configured VerificationService wired to mock, hybrid, or configurable provider."""
    safety_guard = SafetyGuard()

    retriever: EvidenceRetrieverProtocol
    reranker: EvidenceRerankerProtocol
    assessor: EvidenceAssessorProtocol
    explainer: GroundedExplainerProtocol

    if settings.ai_provider == "mock":
        mock_provider = MockPipelineProvider(safety_guard=safety_guard)
        retriever = mock_provider
        reranker = mock_provider
        assessor = mock_provider
        explainer = mock_provider
    else:
        evidence_repo = EvidenceRepository(session=session)
        embedding_provider = get_embedding_provider(settings=settings)
        retriever = HybridPgVectorRetriever(
            evidence_repo=evidence_repo,
            embedding_provider=embedding_provider,
        )
        reranker = _cached_reranker(settings.reranker_backend, settings.reranker_model_name)

        if settings.ai_provider == "configurable":
            llm_provider = ConfigurableLLMAssessorExplainer(
                safety_guard=safety_guard,
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
                model_name=settings.llm_model_name,
                timeout_seconds=settings.llm_timeout_seconds,
                min_confidence_threshold=settings.retrieval_min_score,
            )
            assessor = llm_provider
            explainer = llm_provider
        else:
            assessor = HybridGroundedAssessor(min_confidence_threshold=settings.retrieval_min_score)
            explainer = HybridGroundedExplainer(safety_guard=safety_guard)

    model_version = f"{settings.ai_provider}-{settings.app_version}"
    if settings.ai_provider == "configurable" and settings.llm_base_url and settings.llm_api_key:
        model_version = f"configurable:{settings.llm_model_name}-{settings.app_version}"[:64]

    orchestrator = VerificationPipelineOrchestrator(
        safety_guard=safety_guard,
        claim_extractor=DeterministicClaimExtractor(),
        query_normalizer=IndonesianQueryNormalizer(),
        retriever=retriever,
        reranker=reranker,
        assessor=assessor,
        explainer=explainer,
        citation_validator=ProgrammaticCitationValidator(),
        model_version=model_version,
        min_rerank_score=settings.retrieval_min_score,
    )
    repo = VerificationRepository(session=session)
    return VerificationService(
        orchestrator=orchestrator,
        verification_repo=repo,
        settings=settings,
    )
