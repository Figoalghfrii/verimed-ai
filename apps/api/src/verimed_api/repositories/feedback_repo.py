"""Repository for persisting anonymous user clarity feedback."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.models.feedback import UserFeedback
from verimed_api.models.verification import (
    ClaimAssessment,
    ExtractedClaim,
    VerificationRequest,
)


class FeedbackRepository:
    """Data-access layer for UserFeedback persistence and parent validation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def request_exists(self, request_id: uuid.UUID) -> bool:
        """Return True if the referenced VerificationRequest exists in PostgreSQL."""
        stmt = select(VerificationRequest.id).where(VerificationRequest.id == request_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def assessment_belongs_to_request(
        self,
        assessment_id: uuid.UUID,
        request_id: uuid.UUID,
    ) -> bool:
        """Return True if the ClaimAssessment belongs to the given VerificationRequest."""
        stmt = (
            select(ClaimAssessment.id)
            .join(ExtractedClaim, ClaimAssessment.claim_id == ExtractedClaim.id)
            .where(
                ClaimAssessment.id == assessment_id,
                ExtractedClaim.request_id == request_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_feedback(
        self,
        *,
        feedback_id: uuid.UUID,
        request_id: uuid.UUID,
        assessment_id: uuid.UUID | None,
        is_helpful: bool,
        feedback_category: str | None,
        comment_sanitized: str | None,
    ) -> None:
        """Insert a UserFeedback record and commit the transaction."""
        row = UserFeedback(
            id=feedback_id,
            request_id=request_id,
            assessment_id=assessment_id,
            is_helpful=is_helpful,
            feedback_category=feedback_category,
            comment_sanitized=comment_sanitized,
        )
        self._session.add(row)
        await self._session.commit()
