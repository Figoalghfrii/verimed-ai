"""Repository for persisting and aggregating anonymous user clarity feedback."""

import uuid
from dataclasses import dataclass

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.models.feedback import UserFeedback
from verimed_api.models.verification import (
    ClaimAssessment,
    ExtractedClaim,
    VerificationRequest,
)


@dataclass(frozen=True, slots=True)
class FeedbackStatsSummary:
    """Aggregated counts of anonymous user clarity feedback."""

    total_count: int
    helpful_count: int
    not_helpful_count: int
    by_category: dict[str, int]


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

    async def get_stats(self) -> FeedbackStatsSummary:
        """Return aggregated anonymous feedback counts across all submissions."""
        totals_stmt = select(
            func.count(UserFeedback.id).label("total_count"),
            func.coalesce(
                func.sum(case((UserFeedback.is_helpful.is_(True), 1), else_=0)),
                0,
            ).label("helpful_count"),
        )
        totals_row = (await self._session.execute(totals_stmt)).one()
        total_count = int(totals_row.total_count or 0)
        helpful_count = int(totals_row.helpful_count or 0)
        not_helpful_count = max(0, total_count - helpful_count)

        category_stmt = (
            select(
                UserFeedback.feedback_category,
                func.count(UserFeedback.id).label("category_count"),
            )
            .where(UserFeedback.feedback_category.is_not(None))
            .group_by(UserFeedback.feedback_category)
        )
        category_rows = (await self._session.execute(category_stmt)).all()
        by_category = {
            str(row.feedback_category): int(row.category_count or 0)
            for row in category_rows
            if row.feedback_category
        }

        return FeedbackStatsSummary(
            total_count=total_count,
            helpful_count=helpful_count,
            not_helpful_count=not_helpful_count,
            by_category=by_category,
        )
