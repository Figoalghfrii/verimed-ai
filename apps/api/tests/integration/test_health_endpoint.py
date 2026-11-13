"""Integration tests for GET /api/v1/health endpoint and error envelopes."""

from httpx import AsyncClient


async def test_get_health_endpoint_returns_healthy_envelope(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["meta"]["api_version"] == "v1"
    assert body["meta"]["is_demonstration"] is True

    data = body["data"]
    assert data["status"] == "healthy"
    assert data["service"] == "VeriMed API"
    assert data["ai_provider"] == "mock"
    assert data["database"]["status"] == "connected"
    assert data["database"]["pgvector_enabled"] is True
    assert "bukan alat diagnosis medis" in data["disclaimer"]


async def test_unknown_route_returns_404_json(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/non-existent-route")
    assert response.status_code == 404
