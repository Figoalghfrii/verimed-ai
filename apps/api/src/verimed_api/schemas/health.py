"""Health check endpoint schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class DatabaseHealthStatus(BaseModel):
    """PostgreSQL and pgvector connectivity details."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["connected", "degraded", "disconnected"]
    pgvector_enabled: bool
    latency_ms: float | None = None


class HealthCheckData(BaseModel):
    """Payload returned by GET /api/v1/health."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["healthy", "degraded"]
    service: str
    version: str | None = None
    environment: str | None = None
    ai_provider: str | None = None
    database: DatabaseHealthStatus
    disclaimer: str


class LivenessData(BaseModel):
    """Minimal unprivileged payload returned by GET /api/v1/health/live."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
