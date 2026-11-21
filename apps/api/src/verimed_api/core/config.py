"""Core application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings backed by environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
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

    database_url: str = (
        "postgresql+asyncpg://verimed:verimed_dev_password@localhost:5432/verimed_db"
    )
    database_sync_url: str = (
        "postgresql+psycopg://verimed:verimed_dev_password@localhost:5432/verimed_db"
    )

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
