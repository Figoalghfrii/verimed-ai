"""Pydantic v2 schemas for user clarity feedback endpoints."""

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from verimed_api.core.security import sanitize_user_text

FeedbackCategory = Literal[
    "CLARITY",
    "CITATIONS",
    "ACCURACY_CONCERN",
    "OTHER",
]


class FeedbackRequestInput(BaseModel):
    """Anonymous user rating payload for a completed verification response."""

    model_config = ConfigDict(extra="forbid")

    request_id: uuid.UUID
    assessment_id: uuid.UUID | None = None
    is_helpful: bool
    feedback_category: FeedbackCategory | None = None
    comment: str | None = Field(
        default=None,
        max_length=500,
        description="Optional sanitized feedback comment up to 500 characters.",
    )
    feedback_token: str | None = Field(
        default=None,
        max_length=1024,
        description="Server-issued HMAC token tying feedback to a verification response.",
    )

    @field_validator("comment", mode="before")
    @classmethod
    def sanitize_optional_comment(cls, value: object) -> object:
        if isinstance(value, str):
            cleaned = sanitize_user_text(value)
            return cleaned if cleaned else None
        return value


class FeedbackResponseData(BaseModel):
    """Structured response payload returned by POST /api/v1/feedback."""

    model_config = ConfigDict(extra="forbid")

    feedback_id: str
    request_id: str
    is_helpful: bool
    feedback_category: FeedbackCategory | None = None
    persisted: bool
    message: str


class FeedbackStatsData(BaseModel):
    """Aggregated anonymous user clarity ratings returned by GET /api/v1/feedback/stats."""

    model_config = ConfigDict(extra="forbid")

    total_count: int = Field(..., ge=0)
    helpful_count: int = Field(..., ge=0)
    not_helpful_count: int = Field(..., ge=0)
    helpful_rate: float = Field(..., ge=0.0, le=1.0)
    by_category: dict[str, int] = Field(default_factory=dict)
    database_connected: bool
