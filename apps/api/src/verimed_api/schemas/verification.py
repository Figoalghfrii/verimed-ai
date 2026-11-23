"""Pydantic v2 schemas for claim verification requests and responses."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from verimed_api.core.security import sanitize_user_text
from verimed_api.schemas.evidence import EvidenceSourceItem

VerdictLabel = Literal[
    "SUPPORTED",
    "CONTRADICTED",
    "MIXED_EVIDENCE",
    "INSUFFICIENT_EVIDENCE",
]


class VerificationRequestInput(BaseModel):
    """User-submitted health claim payload."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Health-related claim text in Bahasa Indonesia (10-1000 chars).",
    )
    language: Literal["id", "en"] = "id"

    @field_validator("text", mode="before")
    @classmethod
    def sanitize_and_trim(cls, value: object) -> object:
        if isinstance(value, str):
            return sanitize_user_text(value)
        return value


class EmergencyGuidance(BaseModel):
    """Emergency safety guidance returned when acute medical distress is detected."""

    model_config = ConfigDict(extra="forbid")

    headline: str
    message: str
    emergency_contacts: list[str]


class ClaimVerificationResult(BaseModel):
    """Assessment and grounded evidence for a single extracted claim."""

    model_config = ConfigDict(extra="forbid")

    claim_index: int = Field(..., ge=1)
    assessment_id: str | None = Field(
        default=None,
        description="Persisted claim_assessments UUID when stored in PostgreSQL.",
    )
    claim_text: str
    normalized_query: str
    verdict: VerdictLabel
    verdict_label_id: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    abstained: bool
    abstention_reason: str | None = None
    explanation: str
    uncertainty_notes: str
    citations_valid: bool
    sources: list[EvidenceSourceItem] = Field(default_factory=list)


class VerificationResponseData(BaseModel):
    """Full structured payload returned by POST /api/v1/verify."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    status: Literal["COMPLETED", "EMERGENCY_HALT"]
    language: Literal["id", "en"]
    is_demonstration: bool
    persisted: bool
    emergency_triggered: bool
    emergency_guidance: EmergencyGuidance | None = None
    claims: list[ClaimVerificationResult] = Field(default_factory=list)
    processing_time_ms: int = Field(..., ge=0)
    model_version: str
    disclaimer: str
    feedback_token: str | None = None
