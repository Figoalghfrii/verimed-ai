"""ORM models registry for SQLAlchemy and Alembic."""

from verimed_api.models.base import Base
from verimed_api.models.evidence import (
    Citation,
    EvidenceChunk,
    EvidenceDocument,
    RetrievalResult,
)
from verimed_api.models.feedback import UserFeedback
from verimed_api.models.user import User
from verimed_api.models.verification import (
    ClaimAssessment,
    ExtractedClaim,
    VerificationRequest,
)

__all__ = [
    "Base",
    "User",
    "VerificationRequest",
    "ExtractedClaim",
    "ClaimAssessment",
    "EvidenceDocument",
    "EvidenceChunk",
    "RetrievalResult",
    "Citation",
    "UserFeedback",
]
