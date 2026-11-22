"""End-to-end VeriMed verification pipeline orchestrator."""

from dataclasses import dataclass, field

from verimed_api.pipeline.interfaces import (
    VERDICT_LABELS_ID,
    CitationValidatorProtocol,
    ClaimExtractorProtocol,
    EvidenceAssessorProtocol,
    EvidenceRerankerProtocol,
    EvidenceRetrieverProtocol,
    GroundedExplainerProtocol,
    QueryNormalizerProtocol,
    RetrievedChunkCandidate,
    SafetyGuardProtocol,
)
from verimed_api.schemas.evidence import EvidenceSourceItem
from verimed_api.schemas.verification import ClaimVerificationResult, EmergencyGuidance


@dataclass(frozen=True, slots=True)
class PipelineExecutionOutput:
    """Structured result emitted by the VerificationPipelineOrchestrator."""

    emergency_triggered: bool
    emergency_guidance: EmergencyGuidance | None
    claims: list[ClaimVerificationResult]
    model_version: str
    retrieval_audits: dict[int, list[RetrievedChunkCandidate]] = field(default_factory=dict)


def build_emergency_guidance(language: str = "id") -> EmergencyGuidance:
    """Return immediate emergency medical guidance in Indonesian or English."""
    if language == "en":
        return EmergencyGuidance(
            headline="Potential Acute Medical Emergency Detected",
            message=(
                "Your submission mentions indicators of an acute medical emergency. "
                "VeriMed does not process claim verification in emergency situations. "
                "Please seek immediate professional medical care."
            ),
            emergency_contacts=[
                "Ambulance / Indonesian Ministry of Health: 119",
                "National Emergency Call Center: 112",
                "Visit the nearest Emergency Department (IGD) immediately",
            ],
        )
    return EmergencyGuidance(
        headline="Terdeteksi Potensi Kondisi Darurat Medis",
        message=(
            "Input Anda mengandung indikasi gejala atau kondisi gawat darurat medis. "
            "VeriMed tidak memproses verifikasi klaim untuk situasi darurat. Segera cari "
            "pertolongan medis profesional secara langsung."
        ),
        emergency_contacts=[
            "Ambulans / Kementerian Kesehatan RI: 119",
            "Layanan Darurat Terpadu Nasional: 112",
            "Kunjungi Instalasi Gawat Darurat (IGD) rumah sakit terdekat",
        ],
    )


class VerificationPipelineOrchestrator:
    """Executes all VeriMed verification stages through explicit protocol interfaces."""

    def __init__(
        self,
        safety_guard: SafetyGuardProtocol,
        claim_extractor: ClaimExtractorProtocol,
        query_normalizer: QueryNormalizerProtocol,
        retriever: EvidenceRetrieverProtocol,
        reranker: EvidenceRerankerProtocol,
        assessor: EvidenceAssessorProtocol,
        explainer: GroundedExplainerProtocol,
        citation_validator: CitationValidatorProtocol,
        model_version: str = "mock-0.2.0",
        min_rerank_score: float = 0.35,
    ) -> None:
        self._safety_guard = safety_guard
        self._claim_extractor = claim_extractor
        self._query_normalizer = query_normalizer
        self._retriever = retriever
        self._reranker = reranker
        self._assessor = assessor
        self._explainer = explainer
        self._citation_validator = citation_validator
        self._model_version = model_version
        self._min_rerank_score = min_rerank_score

    async def run(self, raw_text: str, language: str = "id") -> PipelineExecutionOutput:
        """Execute input safety screening, extraction, retrieval, assessment, and citation check."""
        safety = self._safety_guard.screen_input(raw_text)
        if safety.is_emergency:
            return PipelineExecutionOutput(
                emergency_triggered=True,
                emergency_guidance=build_emergency_guidance(language=language),
                claims=[],
                model_version=self._model_version,
            )

        extracted_claims = await self._claim_extractor.extract_claims(safety.sanitized_text)
        results: list[ClaimVerificationResult] = []
        retrieval_audits: dict[int, list[RetrievedChunkCandidate]] = {}

        for idx, claim_text in enumerate(extracted_claims, start=1):
            normalized_query = await self._query_normalizer.normalize(claim_text)
            candidates = await self._retriever.retrieve(
                claim_text=claim_text,
                normalized_query=normalized_query,
                top_k=5,
            )
            reranked = await self._reranker.rerank(
                claim_text=claim_text,
                candidates=candidates,
                min_score=self._min_rerank_score,
            )
            retrieval_audits[idx] = reranked or candidates
            assessment = await self._assessor.assess(
                claim_text=claim_text,
                evidence=reranked,
                language=language,
            )
            draft = await self._explainer.explain(
                claim_text=claim_text,
                assessment=assessment,
                evidence=reranked,
                language=language,
            )
            citations_valid, validated_draft = self._citation_validator.validate(
                draft=draft,
                evidence=reranked,
            )

            sources = [
                EvidenceSourceItem(
                    chunk_id=entry.chunk.chunk_id,
                    citation_key=entry.citation_key,
                    source_name=entry.chunk.source_name,
                    source_type=entry.chunk.source_type,
                    title=entry.chunk.title,
                    source_url=entry.chunk.source_url,
                    publication_date=entry.chunk.publication_date,
                    excerpt=entry.chunk.chunk_text,
                    stance=entry.chunk.stance,
                    relevance_score=round(entry.chunk.rerank_score, 3),
                    is_synthetic_demo=entry.chunk.is_synthetic_demo,
                )
                for entry in validated_draft.citations
            ]

            results.append(
                ClaimVerificationResult(
                    claim_index=idx,
                    claim_text=claim_text,
                    normalized_query=normalized_query,
                    verdict=assessment.verdict,
                    verdict_label_id=VERDICT_LABELS_ID[assessment.verdict],
                    confidence_score=assessment.confidence_score,
                    abstained=assessment.abstained,
                    abstention_reason=assessment.abstention_reason,
                    explanation=validated_draft.explanation,
                    uncertainty_notes=assessment.uncertainty_notes,
                    citations_valid=citations_valid,
                    sources=sources,
                )
            )

        return PipelineExecutionOutput(
            emergency_triggered=False,
            emergency_guidance=None,
            claims=results,
            model_version=self._model_version,
            retrieval_audits=retrieval_audits,
        )
