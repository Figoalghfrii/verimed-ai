"""Integration tests for GET /api/v1/evidence/stats endpoint."""

from httpx import AsyncClient


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
