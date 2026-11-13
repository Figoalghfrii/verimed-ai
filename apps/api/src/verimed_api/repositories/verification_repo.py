"""Repository for persisting verification requests, claims, and assessments."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.models.verification import (
    ClaimAssessment,
    ExtractedClaim,
    VerificationRequest,
)
from verimed_api.pipeline.orchestrator import PipelineExecutionOutput


class VerificationRepository:
    """Persists verification requests and structured claim assessments."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_verification_result(
        self,
        *,
        request_id: uuid.UUID,
        input_text: str,
        language_code: str,
        is_demonstration: bool,
        processing_time_ms: int,
        output: PipelineExecutionOutput,
    ) -> None:
        """Persist a verification request, extracted claims, and assessments."""
        status = "EMERGENCY_HALT" if output.emergency_triggered else "COMPLETED"

        req_row = VerificationRequest(
            id=request_id,
            user_id=None,
            input_text=input_text,
            language_code=language_code,
            status=status,
            is_private=True,
            is_demonstration=is_demonstration,
            emergency_triggered=output.emergency_triggered,
            processing_time_ms=processing_time_ms,
            model_version=output.model_version,
        )
        self._session.add(req_row)

        for claim in output.claims:
            claim_id = uuid.uuid4()
            claim_row = ExtractedClaim(
                id=claim_id,
                request_id=request_id,
                claim_index=claim.claim_index,
                claim_text=claim.claim_text,
                normalized_query=claim.normalized_query,
            )
            self._session.add(claim_row)

            assessment_row = ClaimAssessment(
                claim_id=claim_id,
                verdict=claim.verdict,
                confidence_score=claim.confidence_score,
                abstained=claim.abstained,
                abstention_reason=claim.abstention_reason,
                explanation_text=claim.explanation,
                uncertainty_notes=claim.uncertainty_notes,
                model_name=output.model_version,
                prompt_version="phase2-mvp-v1",
            )
            self._session.add(assessment_row)

        await self._session.commit()
