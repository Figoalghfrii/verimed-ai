"""Core application configuration loaded from environment variables."""

import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = (
    Path(__file__).resolve().parents[5] if len(Path(__file__).resolve().parents) > 5 else Path.cwd()
)
_DEV_EPHEMERAL_CLIENT_SECRET = secrets.token_urlsafe(32)
_DEV_EPHEMERAL_FEEDBACK_SECRET = secrets.token_urlsafe(32)
_INSECURE_SECRET_MARKERS = ("verimed_dev_password", "changeme", ":postgres@", ":password@")


class Settings(BaseSettings):
    """Typed application settings backed by environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=(str(REPO_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "VeriMed API"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    allowed_hosts: list[str] = Field(
        default_factory=lambda: [
            "localhost",
            "127.0.0.1",
            "testserver",
            "api",
            "verimed-api",
            "verimed-web",
        ]
    )
    trusted_proxies: list[str] = Field(default_factory=list)

    expose_api_docs: bool | None = None
    expose_operational_metadata: bool | None = None

    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    verify_rate_limit_requests_per_minute: int = 15
    feedback_rate_limit_requests_per_minute: int = 20
    client_token_rate_limit_requests_per_minute: int = 20
    rate_limit_max_buckets: int = 10_000

    require_client_auth: bool | None = None
    client_auth_secret: str | None = None
    client_api_keys: list[str] = Field(default_factory=list)
    client_token_ttl_seconds: int = 900

    require_feedback_token: bool = True
    feedback_token_secret: str | None = None
    feedback_token_ttl_seconds: int = 86_400

    anonymize_private_claims: bool = True
    data_retention_days: int = 30

    max_concurrent_verifications: int = 8
    llm_daily_call_budget: int = 500
    llm_circuit_breaker_threshold: int = 5
    llm_circuit_breaker_cooldown_seconds: int = 60

    database_url: str | None = None
    database_sync_url: str | None = None

    @field_validator(
        "expose_api_docs",
        "expose_operational_metadata",
        "require_client_auth",
        "client_auth_secret",
        "feedback_token_secret",
        mode="before",
    )
    @classmethod
    def _empty_str_to_none(cls, value: object) -> object:
        """Normalize blank string env vars (e.g. from Compose) to None."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def should_expose_docs(self) -> bool:
        """Expose OpenAPI/Swagger UI only in non-production unless explicitly enabled."""
        if self.expose_api_docs is not None:
            return self.expose_api_docs
        return self.app_env not in {"staging", "production"}

    @property
    def should_expose_operational_metadata(self) -> bool:
        """Expose detailed operational metadata only outside staging/production."""
        if self.expose_operational_metadata is not None:
            return self.expose_operational_metadata
        return self.app_env not in {"staging", "production"}

    @property
    def should_require_client_auth(self) -> bool:
        """Enforce client auth automatically in staging/production unless disabled."""
        if self.require_client_auth is not None:
            return self.require_client_auth
        return self.app_env in {"staging", "production"}

    @property
    def effective_client_auth_secret(self) -> str:
        """Return configured client token signing secret or ephemeral non-prod key."""
        return self.client_auth_secret or _DEV_EPHEMERAL_CLIENT_SECRET

    @property
    def effective_feedback_token_secret(self) -> str:
        """Return configured feedback token signing secret or ephemeral non-prod key."""
        return self.feedback_token_secret or _DEV_EPHEMERAL_FEEDBACK_SECRET

    @model_validator(mode="after")
    def _validate_production_security(self) -> "Settings":
        """Fail fast when staging/production deploys use missing or insecure credentials."""
        if self.app_env not in {"staging", "production"}:
            return self

        for field_name, value in (
            ("database_url", self.database_url),
            ("database_sync_url", self.database_sync_url),
        ):
            if not value or not value.strip():
                raise ValueError(
                    f"{field_name.upper()} must be explicitly configured in {self.app_env}."
                )
            lowered = value.lower()
            if any(marker in lowered for marker in _INSECURE_SECRET_MARKERS):
                raise ValueError(
                    f"{field_name.upper()} contains an insecure default credential "
                    f"in {self.app_env}."
                )

        if "*" in self.cors_origins:
            raise ValueError("Wildcard CORS origin '*' is forbidden in staging/production.")
        if not self.allowed_hosts or "*" in self.allowed_hosts:
            raise ValueError("ALLOWED_HOSTS must list explicit hostnames in staging/production.")

        if self.should_require_client_auth:
            secret_ok = bool(self.client_auth_secret and len(self.client_auth_secret.strip()) >= 16)
            if not secret_ok and not self.client_api_keys:
                raise ValueError(
                    "CLIENT_AUTH_SECRET (>=16 chars) or CLIENT_API_KEYS is required "
                    "in staging/production."
                )

        if self.require_feedback_token and (
            not self.feedback_token_secret or len(self.feedback_token_secret.strip()) < 16
        ):
            raise ValueError(
                "FEEDBACK_TOKEN_SECRET (>=16 chars) is required in staging/production."
            )

        return self

    ai_provider: Literal["mock", "hybrid", "configurable"] = "mock"
    embedding_backend: Literal["hash", "sentence_transformers"] = "hash"
    reranker_backend: Literal["lexical", "cross_encoder"] = "lexical"
    embedding_dimension: int = 768
    embedding_model_name: str = "intfloat/multilingual-e5-base"
    reranker_model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    retrieval_min_score: float = 0.35

    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model_name: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 20.0

    medical_disclaimer_id: str = (
        "VeriMed adalah platform edukasi verifikasi klaim kesehatan berbasis bukti ilmiah, "
        "bukan alat diagnosis medis atau pengganti konsultasi dokter profesional."
    )

    @property
    def is_demonstration_mode(self) -> bool:
        """Returns True when running with synthetic/mock AI provider."""
        return self.ai_provider == "mock"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
