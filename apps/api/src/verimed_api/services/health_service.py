"""Domain service for system health and readiness checks."""

from verimed_api.core.config import Settings
from verimed_api.repositories.health_repo import HealthRepository
from verimed_api.schemas.health import HealthCheckData


class HealthService:
    """Orchestrates application and database readiness reporting."""

    def __init__(self, health_repo: HealthRepository, settings: Settings) -> None:
        self._health_repo = health_repo
        self._settings = settings

    async def get_health_status(self) -> HealthCheckData:
        """Assemble full system health payload."""
        db_status = await self._health_repo.check_database()
        overall_status = (
            "healthy"
            if db_status.status == "connected" and db_status.pgvector_enabled
            else "degraded"
        )
        return HealthCheckData(
            status=overall_status,
            service=self._settings.app_name,
            version=self._settings.app_version,
            environment=self._settings.app_env,
            ai_provider=self._settings.ai_provider,
            database=db_status,
            disclaimer=self._settings.medical_disclaimer_id,
        )
