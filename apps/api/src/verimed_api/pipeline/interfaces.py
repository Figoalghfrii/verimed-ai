"""Protocol interfaces and internal data contracts for the VeriMed AI pipeline."""

from dataclasses import dataclass, field
from datetime import date
from typing import Literal, Protocol

VerdictType = Literal[
    "SUPPORTED",
    "CONTRADICTED",
    "MIXED_EVIDENCE",
    "INSUFFICIENT_EVIDENCE",
]

CitationStanceType = Literal["SUPPORTING", "CONTRADICTING", "CONTEXTUAL"]

VERDICT_LABELS_ID: dict[VerdictType, str] = {
    "SUPPORTED": "Didukung Bukti",
    "CONTRADICTED": "Bertentangan dengan Bukti",
    "MIXED_EVIDENCE": "Bukti Beragam",
    "INSUFFICIENT_EVIDENCE": "Bukti Tidak Cukup",
}


@dataclass(frozen=True, slots=True)
class SafetyCheckResult:
    """Result of pre-pipeline emergency and prompt-injection safety screening."""

    is_emergency: bool
    matched_category: str | None
    sanitized_text: str
    injection_attempts_stripped: int = 0


@dataclass(frozen=True, slots=True)
class RetrievedChunkCandidate:
    """Candidate evidence passage returned from retrieval/reranking."""

    chunk_id: str
    source_name: str
    source_type: str
    title: str
    source_url: str
    publication_date: date | None
    chunk_text: str
    lexical_score: float
    vector_score: float
    hybrid_score: float
    rerank_score: float
    stance: CitationStanceType
    is_synthetic_demo: bool = True


@dataclass(frozen=True, slots=True)
class EvidenceAssessmentResult:
    """Stance assessment and abstention decision for a single claim."""

    verdict: VerdictType
    confidence_score: float
    abstained: bool
    abstention_reason: str | None
    uncertainty_notes: str


@dataclass(frozen=True, slots=True)
class CitationEntry:
    """Validated citation entry linking a citation key to a retrieved chunk."""

    citation_key: str
    chunk: RetrievedChunkCandidate


@dataclass(frozen=True, slots=True)
class ExplanationDraft:
    """Generated grounded explanation before/after citation validation."""

    explanation: str
    citations: list[CitationEntry] = field(default_factory=list)


class SafetyGuardProtocol(Protocol):
    """Screens input for acute medical emergencies and strips prompt injections."""

    def screen_input(self, text: str) -> SafetyCheckResult: ...

    def wrap_untrusted_evidence(self, citation_key: str, text: str) -> str: ...


class ClaimExtractorProtocol(Protocol):
    """Extracts atomic verifiable health claims from user text."""

    async def extract_claims(self, text: str) -> list[str]: ...


class QueryNormalizerProtocol(Protocol):
    """Normalizes colloquial Indonesian health text into search queries."""

    async def normalize(self, claim_text: str) -> str: ...


class EvidenceRetrieverProtocol(Protocol):
    """Retrieves candidate evidence chunks for a normalized query."""

    async def retrieve(
        self,
        claim_text: str,
        normalized_query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunkCandidate]: ...


class EvidenceRerankerProtocol(Protocol):
    """Reranks retrieved evidence candidates and filters below-threshold passages."""

    async def rerank(
        self,
        claim_text: str,
        candidates: list[RetrievedChunkCandidate],
        min_score: float = 0.35,
    ) -> list[RetrievedChunkCandidate]: ...


class EvidenceAssessorProtocol(Protocol):
    """Assesses claim-evidence relationship and enforces abstention gate."""

    async def assess(
        self,
        claim_text: str,
        evidence: list[RetrievedChunkCandidate],
    ) -> EvidenceAssessmentResult: ...


class GroundedExplainerProtocol(Protocol):
    """Generates a grounded explanation in Bahasa Indonesia using untrusted delimiters."""

    async def explain(
        self,
        claim_text: str,
        assessment: EvidenceAssessmentResult,
        evidence: list[RetrievedChunkCandidate],
    ) -> ExplanationDraft: ...


class CitationValidatorProtocol(Protocol):
    """Verifies that every citation marker in an explanation maps to retrieved chunks."""

    def validate(
        self,
        draft: ExplanationDraft,
        evidence: list[RetrievedChunkCandidate],
    ) -> tuple[bool, ExplanationDraft]: ...
