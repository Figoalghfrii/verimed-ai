"""Repository for persisting verification requests, claims, assessments, and citations."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from verimed_api.core.security import redact_private_text
from verimed_api.models.evidence import Citation, RetrievalResult
from verimed_api.models.verification import (
    ClaimAssessment,
    ExtractedClaim,
    VerificationRequest,
)
from verimed_api.pipeline.orchestrator import PipelineExecutionOutput


def _try_parse_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


class VerificationRepository:
    """Persists verification requests, structured claim assessments, and DB citations."""

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
        assessment_ids: dict[int, uuid.UUID] | None = None,
        anonymize_private: bool = False,
    ) -> None:
        """Persist a verification request, extracted claims, assessments, and citations."""
        status = "EMERGENCY_HALT" if output.emergency_triggered else "COMPLETED"
        stored_input_text = redact_private_text(input_text) if anonymize_private else input_text

        req_row = VerificationRequest(
            id=request_id,
            user_id=None,
            input_text=stored_input_text,
            language_code=language_code,
            status=status,
            is_private=True,
            is_demonstration=is_demonstration,
            emergency_triggered=output.emergency_triggered,
            processing_time_ms=processing_time_ms,
            model_version=output.model_version,
        )
        self._session.add(req_row)
        await self._session.flush()

        for claim in output.claims:
            claim_id = uuid.uuid4()
            stored_claim_text = (
                redact_private_text(claim.claim_text) if anonymize_private else claim.claim_text
            )
            stored_norm_query = "" if anonymize_private else claim.normalized_query
            claim_row = ExtractedClaim(
                id=claim_id,
                request_id=request_id,
                claim_index=claim.claim_index,
                claim_text=stored_claim_text,
                normalized_query=stored_norm_query,
            )
            self._session.add(claim_row)
            await self._session.flush()

            audited_candidates = output.retrieval_audits.get(claim.claim_index, [])
            retrieved_now = datetime.now(UTC)
            for rank_pos, candidate in enumerate(audited_candidates, start=1):
                parsed_audit_chunk_id = _try_parse_uuid(candidate.chunk_id)
                if parsed_audit_chunk_id is not None:
                    self._session.add(
                        RetrievalResult(
                            claim_id=claim_id,
                            chunk_id=parsed_audit_chunk_id,
                            lexical_score=candidate.lexical_score,
                            vector_score=candidate.vector_score,
                            hybrid_score=candidate.hybrid_score,
                            rerank_score=candidate.rerank_score,
                            rank_position=rank_pos,
                            retrieved_at=retrieved_now,
                        )
                    )

            assessment_id = (
                assessment_ids.get(claim.claim_index) if assessment_ids is not None else None
            ) or uuid.uuid4()
            assessment_row = ClaimAssessment(
                id=assessment_id,
                claim_id=claim_id,
                verdict=claim.verdict,
                confidence_score=claim.confidence_score,
                abstained=claim.abstained,
                abstention_reason=claim.abstention_reason,
                explanation_text=claim.explanation,
                uncertainty_notes=claim.uncertainty_notes,
                model_name=output.model_version,
                prompt_version="phase3-hybrid-v1",
            )
            self._session.add(assessment_row)
            await self._session.flush()

            for source in claim.sources:
                parsed_chunk_id = _try_parse_uuid(source.chunk_id)
                if parsed_chunk_id is not None:
                    self._session.add(
                        Citation(
                            assessment_id=assessment_id,
                            chunk_id=parsed_chunk_id,
                            citation_key=source.citation_key,
                            stance=source.stance,
                            quoted_span=source.excerpt[:500],
                        )
                    )

        await self._session.commit()

    async def purge_older_than(self, cutoff: datetime) -> int:
        """Delete verification_requests created before `cutoff` and return deleted count."""
        stmt = delete(VerificationRequest).where(VerificationRequest.created_at < cutoff)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return int(result.rowcount or 0)
