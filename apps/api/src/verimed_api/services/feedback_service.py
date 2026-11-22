"""Domain service coordinating user feedback validation, persistence, and stats."""

import logging
import uuid

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from verimed_api.core.exceptions import AppError
from verimed_api.repositories.feedback_repo import FeedbackRepository
from verimed_api.schemas.feedback import (
    FeedbackRequestInput,
    FeedbackResponseData,
    FeedbackStatsData,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    """Validates feedback references and stores anonymous explanation ratings."""

    def __init__(self, feedback_repo: FeedbackRepository) -> None:
        self._feedback_repo = feedback_repo

    async def submit_feedback(self, payload: FeedbackRequestInput) -> FeedbackResponseData:
        """Persist user clarity feedback when DB is available and parent IDs exist."""
        feedback_id = uuid.uuid4()

        try:
            exists = await self._feedback_repo.request_exists(payload.request_id)
        except (SQLAlchemyError, OSError):
            logger.warning(
                "Feedback for request %s received while DB is unavailable.",
                payload.request_id,
            )
            return FeedbackResponseData(
                feedback_id=str(feedback_id),
                request_id=str(payload.request_id),
                is_helpful=payload.is_helpful,
                feedback_category=payload.feedback_category,
                persisted=False,
                message=(
                    "Terima kasih! Masukan Anda dicatat pada sesi ini "
                    "(penyimpanan basis data sedang tidak aktif)."
                ),
            )

        if not exists:
            raise AppError(
                code="VERIFICATION_NOT_FOUND",
                message="Permintaan verifikasi yang dirujuk tidak ditemukan.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if payload.assessment_id is not None:
            valid_assessment = await self._feedback_repo.assessment_belongs_to_request(
                assessment_id=payload.assessment_id,
                request_id=payload.request_id,
            )
            if not valid_assessment:
                raise AppError(
                    code="ASSESSMENT_NOT_FOUND",
                    message=(
                        "Penilaian klaim yang dirujuk tidak sesuai dengan permintaan verifikasi."
                    ),
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        await self._feedback_repo.create_feedback(
            feedback_id=feedback_id,
            request_id=payload.request_id,
            assessment_id=payload.assessment_id,
            is_helpful=payload.is_helpful,
            feedback_category=payload.feedback_category,
            comment_sanitized=payload.comment,
        )

        return FeedbackResponseData(
            feedback_id=str(feedback_id),
            request_id=str(payload.request_id),
            is_helpful=payload.is_helpful,
            feedback_category=payload.feedback_category,
            persisted=True,
            message=(
                "Terima kasih! Masukan Anda membantu meningkatkan kejelasan penjelasan VeriMed."
            ),
        )

    async def get_stats(self) -> FeedbackStatsData:
        """Return aggregated anonymous clarity ratings or zero counts if DB is offline."""
        try:
            summary = await self._feedback_repo.get_stats()
            helpful_rate = (
                round(summary.helpful_count / summary.total_count, 4)
                if summary.total_count > 0
                else 0.0
            )
            return FeedbackStatsData(
                total_count=summary.total_count,
                helpful_count=summary.helpful_count,
                not_helpful_count=summary.not_helpful_count,
                helpful_rate=helpful_rate,
                by_category=summary.by_category,
                database_connected=True,
            )
        except (SQLAlchemyError, OSError):
            logger.warning("Feedback stats requested while DB is unavailable.")
            return FeedbackStatsData(
                total_count=0,
                helpful_count=0,
                not_helpful_count=0,
                helpful_rate=0.0,
                by_category={},
                database_connected=False,
            )
