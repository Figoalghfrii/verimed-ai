"""Domain service for system health and readiness checks."""

from verimed_api.core.config import Settings
from verimed_api.repositories.health_repo import HealthRepository
from verimed_api.schemas.health import DatabaseHealthStatus, HealthCheckData


class HealthService:
    """Orchestrates application and database readiness reporting."""

    def __init__(self, health_repo: HealthRepository, settings: Settings) -> None:
        self._health_repo = health_repo
        self._settings = settings

    async def get_health_status(self) -> HealthCheckData:
        """Assemble system health payload with environment-appropriate redaction."""
        db_status = await self._health_repo.check_database()
        overall_status = (
            "healthy"
            if db_status.status == "connected" and db_status.pgvector_enabled
            else "degraded"
        )
        expose_meta = self._settings.should_expose_operational_metadata
        safe_db_status = (
            db_status
            if expose_meta
            else DatabaseHealthStatus(
                status=db_status.status,
                pgvector_enabled=db_status.pgvector_enabled,
                latency_ms=None,
            )
        )
        return HealthCheckData(
            status=overall_status,
            service=self._settings.app_name,
            version=self._settings.app_version if expose_meta else None,
            environment=self._settings.app_env if expose_meta else None,
            ai_provider=self._settings.ai_provider if expose_meta else None,
            database=safe_db_status,
            disclaimer=self._settings.medical_disclaimer_id,
        )
