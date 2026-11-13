"""Repository for checking PostgreSQL and pgvector extension readiness."""

import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.schemas.health import DatabaseHealthStatus


class HealthRepository:
    """Executes lightweight database liveness and pgvector checks."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def check_database(self) -> DatabaseHealthStatus:
        """Verify PostgreSQL connectivity and pgvector extension presence."""
        start_time = time.perf_counter()
        try:
            await self._session.execute(text("SELECT 1"))
            ext_result = await self._session.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            pgvector_enabled = bool(ext_result.scalar())
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return DatabaseHealthStatus(
                status="connected" if pgvector_enabled else "degraded",
                pgvector_enabled=pgvector_enabled,
                latency_ms=latency_ms,
            )
        except Exception:
            return DatabaseHealthStatus(
                status="disconnected",
                pgvector_enabled=False,
                latency_ms=None,
            )
