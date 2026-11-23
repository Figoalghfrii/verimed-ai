"""Security hardening constraints, feedback uniqueness indexes, and app role grants."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_security_hardening"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add data integrity check constraints, deduplication indexes, and least-privilege grants."""
    op.create_check_constraint(
        "ck_claim_assessments_confidence_range",
        "claim_assessments",
        "confidence_score >= 0.0 AND confidence_score <= 1.0",
    )
    op.create_check_constraint(
        "ck_claim_assessments_verdict_enum",
        "claim_assessments",
        "verdict IN ('SUPPORTED', 'CONTRADICTED', 'MIXED_EVIDENCE', 'INSUFFICIENT_EVIDENCE')",
    )
    op.create_check_constraint(
        "ck_retrieval_results_rank_positive",
        "retrieval_results",
        "rank_position >= 1",
    )

    op.execute(
        """
        DELETE FROM user_feedback a
        USING user_feedback b
        WHERE a.id > b.id
          AND a.request_id = b.request_id
          AND (
            (a.assessment_id IS NOT NULL AND a.assessment_id = b.assessment_id)
            OR (a.assessment_id IS NULL AND b.assessment_id IS NULL)
          );
        """
    )

    op.create_index(
        "uq_user_feedback_request_assessment",
        "user_feedback",
        ["request_id", "assessment_id"],
        unique=True,
        postgresql_where=sa.text("assessment_id IS NOT NULL"),
    )
    op.create_index(
        "uq_user_feedback_request_only",
        "user_feedback",
        ["request_id"],
        unique=True,
        postgresql_where=sa.text("assessment_id IS NULL"),
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'verimed_app') THEN
                GRANT USAGE ON SCHEMA public TO verimed_app;
                GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO verimed_app;
                GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO verimed_app;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    """Revert security hardening indexes and check constraints."""
    op.drop_index("uq_user_feedback_request_only", table_name="user_feedback")
    op.drop_index("uq_user_feedback_request_assessment", table_name="user_feedback")
    op.drop_constraint("ck_retrieval_results_rank_positive", "retrieval_results", type_="check")
    op.drop_constraint("ck_claim_assessments_verdict_enum", "claim_assessments", type_="check")
    op.drop_constraint("ck_claim_assessments_confidence_range", "claim_assessments", type_="check")
