"""Unit tests for schemas, security utilities, and ORM metadata."""

from verimed_api.core.security import is_safe_external_url, sanitize_user_text
from verimed_api.models import Base
from verimed_api.schemas.common import ApiResponse, ErrorBody, ErrorDetail, ErrorResponse


def test_sanitize_user_text_strips_control_chars() -> None:
    raw = "  Klaim kesehatan\x00\x07 dengan karakter kontrol  "
    assert sanitize_user_text(raw) == "Klaim kesehatan dengan karakter kontrol"


def test_ssrf_guard_blocks_private_and_non_https_urls() -> None:
    assert is_safe_external_url("http://who.int/news") is False
    assert is_safe_external_url("https://localhost/admin") is False
    assert is_safe_external_url("https://127.0.0.1/secret") is False
    assert is_safe_external_url("https://169.254.169.254/latest/meta-data") is False
    assert is_safe_external_url("https://www.who.int/health-topics") is True


def test_api_and_error_response_envelopes() -> None:
    resp = ApiResponse[dict[str, str]](data={"hello": "world"})
    assert resp.success is True
    assert resp.data["hello"] == "world"
    assert resp.meta.api_version == "v1"
    assert resp.meta.is_demonstration is True

    err = ErrorResponse(
        error=ErrorBody(
            code="INVALID_INPUT",
            message="Invalid input",
            details=[ErrorDetail(field="text", issue="Too short")],
        )
    )
    assert err.success is False
    assert err.error.code == "INVALID_INPUT"


def test_sqlalchemy_metadata_contains_all_nine_core_tables() -> None:
    expected_tables = {
        "users",
        "verification_requests",
        "extracted_claims",
        "evidence_documents",
        "evidence_chunks",
        "retrieval_results",
        "claim_assessments",
        "citations",
        "user_feedback",
    }
    assert expected_tables.issubset(set(Base.metadata.tables.keys()))
