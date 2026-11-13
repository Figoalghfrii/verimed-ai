"""Verification requests, extracted claims, and claim assessments models."""

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from verimed_api.models.base import Base, TimestampUUIDMixin


class VerificationRequest(TimestampUUIDMixin, Base):
    """Represents a user's health claim verification submission."""

    __tablename__ = "verification_requests"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), default="id", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_demonstration: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    emergency_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_version: Mapped[str] = mapped_column(String(64), default="mock-0.1.0", nullable=False)

    claims: Mapped[list["ExtractedClaim"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )


class ExtractedClaim(TimestampUUIDMixin, Base):
    """Atomic verifiable health claim decomposed from a verification request."""

    __tablename__ = "extracted_claims"

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("verification_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    claim_index: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_query: Mapped[str] = mapped_column(Text, nullable=False)

    request: Mapped["VerificationRequest"] = relationship(back_populates="claims")
    assessment: Mapped["ClaimAssessment | None"] = relationship(
        back_populates="claim",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ClaimAssessment(TimestampUUIDMixin, Base):
    """Evaluation verdict and grounded explanation for an extracted claim."""

    __tablename__ = "claim_assessments"

    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("extracted_claims.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    verdict: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    abstention_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)
    uncertainty_notes: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)

    claim: Mapped["ExtractedClaim"] = relationship(back_populates="assessment")
