"""User feedback model for explanation clarity ratings."""

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from verimed_api.models.base import Base, TimestampUUIDMixin


class UserFeedback(TimestampUUIDMixin, Base):
    """Anonymous user feedback on verification explanations."""

    __tablename__ = "user_feedback"

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("verification_requests.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("claim_assessments.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    comment_sanitized: Mapped[str | None] = mapped_column(String(500), nullable=True)
