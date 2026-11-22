"""Domain service coordinating health claim verification and persistence."""

import logging
import time
import uuid

from verimed_api.core.config import Settings
from verimed_api.pipeline.orchestrator import VerificationPipelineOrchestrator
from verimed_api.repositories.verification_repo import VerificationRepository
from verimed_api.schemas.verification import (
    VerificationRequestInput,
    VerificationResponseData,
)

logger = logging.getLogger(__name__)


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
        """Run AI verification pipeline and attempt best-effort persistence."""
        request_id = uuid.uuid4()
        start = time.perf_counter()

        output = await self._orchestrator.run(payload.text, language=payload.language)
        processing_time_ms = max(1, int((time.perf_counter() - start) * 1000))

        uses_synthetic_sources = any(
            src.is_synthetic_demo for claim in output.claims for src in claim.sources
        )
        is_demo = self._settings.is_demonstration_mode or uses_synthetic_sources

        persisted = False
        try:
            await self._verification_repo.save_verification_result(
                request_id=request_id,
                input_text=payload.text,
                language_code=payload.language,
                is_demonstration=is_demo,
                processing_time_ms=processing_time_ms,
                output=output,
            )
            persisted = True
        except Exception:
            # Never log raw user health claim text; record only request_id.
            logger.warning(
                "Verification request %s completed without DB persistence (DB unavailable).",
                request_id,
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
            claims=output.claims,
            processing_time_ms=processing_time_ms,
            model_version=output.model_version,
            disclaimer=disclaimer,
        )
