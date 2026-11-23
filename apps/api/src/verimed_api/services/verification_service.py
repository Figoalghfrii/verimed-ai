"""Domain service coordinating health claim verification and persistence."""

import asyncio
import logging
import time
import uuid

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from verimed_api.core.config import Settings
from verimed_api.core.exceptions import AppError
from verimed_api.core.logging import log_security_event
from verimed_api.core.security import issue_signed_token
from verimed_api.pipeline.orchestrator import VerificationPipelineOrchestrator
from verimed_api.repositories.verification_repo import VerificationRepository
from verimed_api.schemas.verification import (
    VerificationRequestInput,
    VerificationResponseData,
)

logger = logging.getLogger(__name__)
_LOOP_SEMAPHORES: dict[tuple[int, int], asyncio.Semaphore] = {}


def _get_verification_semaphore(limit: int) -> asyncio.Semaphore:
    """Return an event-loop-scoped Semaphore limiting concurrent verification runs."""
    loop_key = (id(asyncio.get_running_loop()), max(1, limit))
    semaphore = _LOOP_SEMAPHORES.get(loop_key)
    if semaphore is None:
        if len(_LOOP_SEMAPHORES) > 64:
            _LOOP_SEMAPHORES.clear()
        semaphore = asyncio.Semaphore(max(1, limit))
        _LOOP_SEMAPHORES[loop_key] = semaphore
    return semaphore


class VerificationService:
    """Orchestrates claim verification execution and privacy-safe persistence."""

    def __init__(
        self,
        orchestrator: VerificationPipelineOrchestrator,
        verification_repo: VerificationRepository,
        settings: Settings,
    ) -> None:
        self._orchestrator = orchestrator
        self._verification_repo = verification_repo
        self._settings = settings

    async def verify_claim(self, payload: VerificationRequestInput) -> VerificationResponseData:
        """Run AI verification pipeline and attempt best-effort privacy-safe persistence."""
        request_id = uuid.uuid4()
        start = time.perf_counter()
        semaphore = _get_verification_semaphore(self._settings.max_concurrent_verifications)

        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=1.0)
        except TimeoutError as exc:
            log_security_event(
                "verification_concurrency_exhausted",
                request_id=str(request_id),
                outcome="rejected",
                details={"limit": self._settings.max_concurrent_verifications},
            )
            raise AppError(
                code="SERVICE_BUSY",
                message="Layanan sedang memproses banyak permintaan. Silakan coba lagi sesaat.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from exc

        try:
            output = await self._orchestrator.run(payload.text, language=payload.language)
        finally:
            semaphore.release()

        processing_time_ms = max(1, int((time.perf_counter() - start) * 1000))

        uses_synthetic_sources = any(
            src.is_synthetic_demo for claim in output.claims for src in claim.sources
        )
        is_demo = self._settings.is_demonstration_mode or uses_synthetic_sources

        persisted = False
        claims_with_ids = output.claims
        assessment_ids_by_index = {claim.claim_index: uuid.uuid4() for claim in output.claims}
        try:
            await self._verification_repo.save_verification_result(
                request_id=request_id,
                input_text=payload.text,
                language_code=payload.language,
                is_demonstration=is_demo,
                processing_time_ms=processing_time_ms,
                output=output,
                assessment_ids=assessment_ids_by_index,
                anonymize_private=self._settings.anonymize_private_claims,
            )
            persisted = True
            claims_with_ids = [
                claim.model_copy(
                    update={"assessment_id": str(assessment_ids_by_index[claim.claim_index])}
                )
                for claim in output.claims
            ]
        except (SQLAlchemyError, OSError):
            # Never log raw user health claim text; record only request_id and traceback.
            logger.warning(
                "Verification request %s completed without DB persistence (DB unavailable).",
                request_id,
                exc_info=True,
            )

        feedback_token: str | None = None
        if not output.emergency_triggered:
            feedback_token = issue_signed_token(
                payload={
                    "request_id": str(request_id),
                    "assessment_ids": [str(val) for val in assessment_ids_by_index.values()],
                },
                secret=self._settings.effective_feedback_token_secret,
                ttl_seconds=self._settings.feedback_token_ttl_seconds,
            )

        disclaimer = (
            "VeriMed is an educational evidence-based health claim verification platform, "
            "not a medical diagnosis tool or a substitute for professional medical consultation."
            if payload.language == "en"
            else self._settings.medical_disclaimer_id
        )

        return VerificationResponseData(
            request_id=str(request_id),
            status="EMERGENCY_HALT" if output.emergency_triggered else "COMPLETED",
            language=payload.language,
            is_demonstration=is_demo,
            persisted=persisted,
            emergency_triggered=output.emergency_triggered,
            emergency_guidance=output.emergency_guidance,
            claims=claims_with_ids,
            processing_time_ms=processing_time_ms,
            model_version=output.model_version,
            disclaimer=disclaimer,
            feedback_token=feedback_token,
        )
