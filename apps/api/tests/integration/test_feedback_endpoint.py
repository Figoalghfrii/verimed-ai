"""Integration tests for POST /api/v1/feedback and FeedbackService fallback."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from verimed_api.core.config import get_settings
from verimed_api.core.security import issue_signed_token
from verimed_api.schemas.feedback import FeedbackRequestInput
from verimed_api.services.feedback_service import FeedbackService


async def test_submit_feedback_for_verified_request_returns_201(
    async_client: AsyncClient,
) -> None:
    """Submitting feedback with a valid feedback_token returns 201 and blocks duplicates."""
    verify_res = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Mencuci tangan pakai sabun membantu mencegah penularan infeksi.",
            "language": "id",
        },
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()["data"]
    request_id = verify_data["request_id"]
    feedback_token = verify_data["feedback_token"]
    assert isinstance(feedback_token, str) and "." in feedback_token

    feedback_res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": request_id,
            "is_helpful": True,
            "feedback_category": "CLARITY",
            "comment": "  Penjelasan sangat jelas\x00 dan mudah dipahami.  ",
            "feedback_token": feedback_token,
        },
    )
    assert feedback_res.status_code == 201
    payload = feedback_res.json()
    assert payload["success"] is True
    assert payload["data"]["request_id"] == request_id
    assert payload["data"]["is_helpful"] is True
    assert payload["data"]["feedback_category"] == "CLARITY"
    assert payload["data"]["persisted"] is True

    duplicate_res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": request_id,
            "is_helpful": False,
            "feedback_category": "CITATIONS",
            "feedback_token": feedback_token,
        },
    )
    assert duplicate_res.status_code == 409
    assert duplicate_res.json()["error"]["code"] == "DUPLICATE_FEEDBACK"


async def test_submit_feedback_without_or_with_forged_token_returns_403(
    async_client: AsyncClient,
) -> None:
    """Submitting feedback without a valid server-signed token is rejected with 403."""
    unknown_id = str(uuid.uuid4())
    missing_res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": unknown_id,
            "is_helpful": False,
            "feedback_category": "CITATIONS",
        },
    )
    assert missing_res.status_code == 403
    assert missing_res.json()["error"]["code"] == "INVALID_FEEDBACK_TOKEN"

    forged_res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": unknown_id,
            "is_helpful": False,
            "feedback_category": "CITATIONS",
            "feedback_token": "tampered.token",
        },
    )
    assert forged_res.status_code == 403
    assert forged_res.json()["error"]["code"] == "INVALID_FEEDBACK_TOKEN"


async def test_submit_feedback_for_unknown_request_returns_404(
    async_client: AsyncClient,
) -> None:
    """Submitting validly signed feedback for an unknown request_id returns 404 ErrorResponse."""
    unknown_id = str(uuid.uuid4())
    valid_token = issue_signed_token(
        payload={"request_id": unknown_id, "assessment_ids": []},
        secret=get_settings().effective_feedback_token_secret,
        ttl_seconds=600,
    )
    res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": unknown_id,
            "is_helpful": False,
            "feedback_category": "CITATIONS",
            "feedback_token": valid_token,
        },
    )
    assert res.status_code == 404
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VERIFICATION_NOT_FOUND"


async def test_submit_feedback_invalid_payload_returns_422_envelope(
    async_client: AsyncClient,
) -> None:
    """Invalid UUID or comment exceeding 500 chars triggers standard VALIDATION_ERROR."""
    res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": "not-a-uuid",
            "is_helpful": True,
            "comment": "x" * 501,
        },
    )
    assert res.status_code == 422
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


class _OfflineFeedbackRepo:
    async def request_exists(self, request_id: uuid.UUID) -> bool:
        del request_id
        raise OperationalError("SELECT 1", {}, Exception("DB offline"))


@pytest.mark.asyncio
async def test_feedback_service_returns_unpersisted_when_db_offline() -> None:
    """FeedbackService degrades gracefully with persisted=False if DB is unavailable."""
    service = FeedbackService(feedback_repo=_OfflineFeedbackRepo())  # type: ignore[arg-type]
    req_id = uuid.uuid4()
    token = issue_signed_token(
        payload={"request_id": str(req_id), "assessment_ids": []},
        secret=get_settings().effective_feedback_token_secret,
        ttl_seconds=600,
    )
    result = await service.submit_feedback(
        FeedbackRequestInput(
            request_id=req_id,
            is_helpful=True,
            feedback_category="OTHER",
            comment="Bagus",
            feedback_token=token,
        )
    )
    assert result.request_id == str(req_id)
    assert result.persisted is False


async def test_get_feedback_stats_aggregates_submissions(
    async_client: AsyncClient,
) -> None:
    """GET /api/v1/feedback/stats aggregates anonymous clarity ratings."""
    verify_res_1 = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Mencuci tangan pakai sabun membantu mencegah penularan infeksi.",
            "language": "id",
        },
    )
    verify_res_2 = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Imunisasi anak membantu mencegah penyakit infeksi berbahaya.",
            "language": "id",
        },
    )
    d1 = verify_res_1.json()["data"]
    d2 = verify_res_2.json()["data"]

    await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": d1["request_id"],
            "is_helpful": True,
            "feedback_category": "CLARITY",
            "feedback_token": d1["feedback_token"],
        },
    )
    await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": d2["request_id"],
            "is_helpful": False,
            "feedback_category": "CITATIONS",
            "feedback_token": d2["feedback_token"],
        },
    )

    stats_res = await async_client.get("/api/v1/feedback/stats")
    assert stats_res.status_code == 200
    data = stats_res.json()["data"]
    assert data["total_count"] == 2
    assert data["helpful_count"] == 1
    assert data["not_helpful_count"] == 1
    assert data["helpful_rate"] == 0.5
    assert data["by_category"] == {"CLARITY": 1, "CITATIONS": 1}
    assert data["database_connected"] is True
