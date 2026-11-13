"""Initial VeriMed relational schema and pgvector extension.

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-10-31 12:20:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create pgvector extension and core VeriMed tables."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email_hash", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="public"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email_hash", "users", ["email_hash"], unique=True)

    op.create_table(
        "verification_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("language_code", sa.String(length=10), nullable=False, server_default="id"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "is_demonstration",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "emergency_triggered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "model_version",
            sa.String(length=64),
            nullable=False,
            server_default="mock-0.1.0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_verification_requests_user_id", "verification_requests", ["user_id"])
    op.create_index("ix_verification_requests_status", "verification_requests", ["status"])

    op.create_table(
        "extracted_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("verification_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("claim_index", sa.Integer(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("normalized_query", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_extracted_claims_request_id", "extracted_claims", ["request_id"])

    op.create_table(
        "evidence_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", sa.Text(), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("language_code", sa.String(length=10), nullable=False, server_default="id"),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_synthetic_demo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_evidence_documents_source_name", "evidence_documents", ["source_name"])
    op.create_index(
        "ix_evidence_documents_publication_date",
        "evidence_documents",
        ["publication_date"],
    )
    op.create_index("ix_evidence_documents_source_type", "evidence_documents", ["source_type"])
    op.create_index(
        "ix_evidence_documents_content_hash",
        "evidence_documents",
        ["content_hash"],
        unique=True,
    )

    op.create_table(
        "evidence_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("evidence_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("content_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_evidence_chunks_document_id", "evidence_chunks", ["document_id"])
    op.create_index(
        "ix_evidence_chunks_search_vector",
        "evidence_chunks",
        ["search_vector"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_evidence_chunks_embedding_hnsw",
        "evidence_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    op.create_table(
        "retrieval_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "claim_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("extracted_claims.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "chunk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("evidence_chunks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("lexical_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("vector_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("hybrid_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("rerank_score", sa.Float(), nullable=True),
        sa.Column("rank_position", sa.Integer(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_retrieval_results_claim_id", "retrieval_results", ["claim_id"])
    op.create_index("ix_retrieval_results_chunk_id", "retrieval_results", ["chunk_id"])

    op.create_table(
        "claim_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "claim_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("extracted_claims.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("verdict", sa.String(length=32), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("abstained", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("abstention_reason", sa.Text(), nullable=True),
        sa.Column("explanation_text", sa.Text(), nullable=False),
        sa.Column("uncertainty_notes", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_claim_assessments_claim_id", "claim_assessments", ["claim_id"], unique=True)
    op.create_index("ix_claim_assessments_verdict", "claim_assessments", ["verdict"])

    op.create_table(
        "citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("claim_assessments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "chunk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("evidence_chunks.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("citation_key", sa.String(length=16), nullable=False),
        sa.Column("stance", sa.String(length=32), nullable=False),
        sa.Column("quoted_span", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_citations_assessment_id", "citations", ["assessment_id"])
    op.create_index("ix_citations_chunk_id", "citations", ["chunk_id"])

    op.create_table(
        "user_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("verification_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("claim_assessments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_helpful", sa.Boolean(), nullable=False),
        sa.Column("feedback_category", sa.String(length=64), nullable=True),
        sa.Column("comment_sanitized", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_user_feedback_request_id", "user_feedback", ["request_id"])
    op.create_index("ix_user_feedback_assessment_id", "user_feedback", ["assessment_id"])


def downgrade() -> None:
    """Drop core VeriMed tables."""
    op.drop_table("user_feedback")
    op.drop_table("citations")
    op.drop_table("claim_assessments")
    op.drop_table("retrieval_results")
    op.drop_table("evidence_chunks")
    op.drop_table("evidence_documents")
    op.drop_table("extracted_claims")
    op.drop_table("verification_requests")
    op.drop_table("users")
