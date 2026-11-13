"""FastAPI dependency injection providers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.core.config import Settings, get_settings
from verimed_api.core.database import get_db_session
from verimed_api.pipeline.citation_validator import ProgrammaticCitationValidator
from verimed_api.pipeline.claim_extractor import DeterministicClaimExtractor
from verimed_api.pipeline.orchestrator import VerificationPipelineOrchestrator
from verimed_api.pipeline.providers.mock_provider import MockPipelineProvider
from verimed_api.pipeline.query_normalizer import IndonesianQueryNormalizer
from verimed_api.pipeline.safety_guard import SafetyGuard
from verimed_api.repositories.health_repo import HealthRepository
from verimed_api.repositories.verification_repo import VerificationRepository
from verimed_api.services.health_service import HealthService
from verimed_api.services.verification_service import VerificationService

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_health_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> HealthService:
    """Provide configured HealthService instance."""
    repo = HealthRepository(session=session)
    return HealthService(health_repo=repo, settings=settings)


def get_verification_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> VerificationService:
    """Provide configured VerificationService wired to the active AI pipeline provider."""
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
        model_version=f"{settings.ai_provider}-{settings.app_version}",
    )
    repo = VerificationRepository(session=session)
    return VerificationService(
        orchestrator=orchestrator,
        verification_repo=repo,
        settings=settings,
    )
