"""Integration tests for GET /api/v1/evidence/stats endpoint."""

from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from verimed_api.pipeline.providers.embedding_provider import DeterministicHashEmbeddingProvider
from verimed_api.services.ingestion_service import IngestionService


async def test_get_evidence_stats_returns_corpus_counts(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/api/v1/evidence/stats")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["documents_count"] == 5
    assert data["chunks_count"] == 10
    assert data["synthetic_documents_count"] == 5
    assert data["ai_provider"] == "mock"
    assert data["embedding_backend"] == "hash"
    assert data["reranker_backend"] == "lexical"


async def test_ingestion_service_get_stats_returns_zeros_when_db_offline() -> None:
    class _OfflineEvidenceRepo:
        async def get_corpus_stats(self) -> object:
            raise OperationalError("SELECT 1", {}, Exception("DB offline"))

    service = IngestionService(
        evidence_repo=_OfflineEvidenceRepo(),  # type: ignore[arg-type]
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )
    stats = await service.get_stats()
    assert stats.documents_count == 0
    assert stats.chunks_count == 0
    assert stats.synthetic_documents_count == 0


async def test_list_evidence_documents_supports_filters_and_pagination(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/api/v1/evidence/documents")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2
    assert body["data"]["database_connected"] is True

    curated_only = await async_client.get(
        "/api/v1/evidence/documents",
        params={"include_synthetic": "false", "q": "Kementerian"},
    )
    assert curated_only.status_code == 200
    curated_data = curated_only.json()["data"]
    assert curated_data["total"] == 1
    assert curated_data["items"][0]["is_synthetic_demo"] is False
    assert curated_data["items"][0]["source_name"] == "Kementerian Kesehatan RI"


async def test_ingestion_service_list_documents_falls_back_when_db_offline() -> None:
    class _OfflineEvidenceRepo:
        async def list_documents(self, **_kwargs: object) -> tuple[list[object], int]:
            raise OperationalError("SELECT 1", {}, Exception("DB offline"))

    service = IngestionService(
        evidence_repo=_OfflineEvidenceRepo(),  # type: ignore[arg-type]
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )
    items, total, connected = await service.list_documents(search="kemenkes")
    assert items == []
    assert total == 0
    assert connected is False
