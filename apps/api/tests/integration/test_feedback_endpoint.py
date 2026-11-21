"""Integration tests for POST /api/v1/feedback and FeedbackService fallback."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from verimed_api.schemas.feedback import FeedbackRequestInput
from verimed_api.services.feedback_service import FeedbackService


async def test_submit_feedback_for_verified_request_returns_201(
    async_client: AsyncClient,
) -> None:
    """Submitting feedback for a persisted verification request returns 201."""
    verify_res = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Mencuci tangan pakai sabun membantu mencegah penularan infeksi.",
            "language": "id",
        },
    )
    assert verify_res.status_code == 200
    request_id = verify_res.json()["data"]["request_id"]

    feedback_res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": request_id,
            "is_helpful": True,
            "feedback_category": "CLARITY",
            "comment": "  Penjelasan sangat jelas\x00 dan mudah dipahami.  ",
        },
    )
    assert feedback_res.status_code == 201
    payload = feedback_res.json()
    assert payload["success"] is True
    assert payload["data"]["request_id"] == request_id
    assert payload["data"]["is_helpful"] is True
    assert payload["data"]["feedback_category"] == "CLARITY"
    assert payload["data"]["persisted"] is True


async def test_submit_feedback_for_unknown_request_returns_404(
    async_client: AsyncClient,
) -> None:
    """Submitting feedback for an unknown request_id returns 404 ErrorResponse."""
    unknown_id = str(uuid.uuid4())
    res = await async_client.post(
        "/api/v1/feedback",
        json={
            "request_id": unknown_id,
            "is_helpful": False,
            "feedback_category": "CITATIONS",
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
    result = await service.submit_feedback(
        FeedbackRequestInput(
            request_id=req_id,
            is_helpful=True,
            feedback_category="OTHER",
            comment="Bagus",
        )
    )
    assert result.request_id == str(req_id)
    assert result.persisted is False
