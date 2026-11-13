"""FastAPI dependency injection providers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.core.config import Settings, get_settings
from verimed_api.core.database import get_db_session
from verimed_api.repositories.health_repo import HealthRepository
from verimed_api.services.health_service import HealthService

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_health_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> HealthService:
    """Provide configured HealthService instance."""
    repo = HealthRepository(session=session)
    return HealthService(health_repo=repo, settings=settings)
