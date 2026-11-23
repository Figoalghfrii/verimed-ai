"""Live PostgreSQL + pgvector integration tests (executed when VERIMED_TEST_DATABASE_URL is set)."""

import os
import uuid

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from verimed_api.core.config import Settings
from verimed_api.core.exceptions import AppError
from verimed_api.models.evidence import EvidenceChunk, EvidenceDocument
from verimed_api.models.verification import VerificationRequest
from verimed_api.pipeline.citation_validator import ProgrammaticCitationValidator
from verimed_api.pipeline.claim_extractor import DeterministicClaimExtractor
from verimed_api.pipeline.orchestrator import VerificationPipelineOrchestrator
from verimed_api.pipeline.providers.embedding_provider import DeterministicHashEmbeddingProvider
from verimed_api.pipeline.providers.hybrid_grounded_provider import (
    HybridGroundedAssessor,
    HybridGroundedExplainer,
)
from verimed_api.pipeline.query_normalizer import IndonesianQueryNormalizer
from verimed_api.pipeline.reranker import LexicalOverlapReranker
from verimed_api.pipeline.retriever import HybridPgVectorRetriever
from verimed_api.pipeline.safety_guard import SafetyGuard
from verimed_api.repositories.evidence_repo import EvidenceRepository
from verimed_api.repositories.feedback_repo import FeedbackRepository
from verimed_api.repositories.verification_repo import VerificationRepository
from verimed_api.schemas.feedback import FeedbackRequestInput
from verimed_api.schemas.verification import VerificationRequestInput
from verimed_api.services.feedback_service import FeedbackService
from verimed_api.services.ingestion_service import IngestionDocumentInput, IngestionService
from verimed_api.services.verification_service import VerificationService

TEST_DB_URL = os.getenv("VERIMED_TEST_DATABASE_URL")


@pytest.mark.skipif(
    not TEST_DB_URL,
    reason=(
        "VERIMED_TEST_DATABASE_URL is not set; skipping live PostgreSQL pgvector integration test."
    ),
)
async def test_postgres_pgvector_end_to_end_reembed_verify_and_feedback() -> None:
    """Verify ingestion, force_reembed, hybrid RRF retrieval, persistence, and feedback FK."""
    assert TEST_DB_URL is not None
    engine = create_async_engine(TEST_DB_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    unique_marker = uuid.uuid4().hex[:10]
    created_doc_id: uuid.UUID | None = None
    created_request_id: uuid.UUID | None = None

    try:
        async with session_factory() as session:
            evidence_repo = EvidenceRepository(session=session)
            embedder = DeterministicHashEmbeddingProvider(dimension=768)
            ingestion = IngestionService(evidence_repo=evidence_repo, embedding_provider=embedder)

            doc_input = IngestionDocumentInput(
                source_name="VeriMed Integration Suite",
                source_url=f"https://demo.verimed.local/integration/{unique_marker}",
                title=f"Uji Integrasi Cuci Tangan {unique_marker}",
                body_text=(
                    f"Kode uji {unique_marker}: Cuci tangan pakai sabun terbukti efektif "
                    "mencegah penularan diare dan infeksi pernapasan."
                ),
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                is_synthetic_demo=True,
            )
            doc_id, created_new = await ingestion.ingest_document(doc_input)
            created_doc_id = doc_id
            assert created_new is True

            # Verify force_reembed preserves existing chunk UUIDs while incrementing version
            first_chunk_id = await session.scalar(
                select(EvidenceChunk.id).where(EvidenceChunk.document_id == doc_id)
            )
            doc_id_2, created_second = await ingestion.ingest_document(
                doc_input, force_reembed=True
            )
            assert doc_id_2 == doc_id
            assert created_second is False
            reembedded_chunk = await session.get(EvidenceChunk, first_chunk_id)
            assert reembedded_chunk is not None
            assert reembedded_chunk.content_version == 2

            safety_guard = SafetyGuard()
            orchestrator = VerificationPipelineOrchestrator(
                safety_guard=safety_guard,
                claim_extractor=DeterministicClaimExtractor(),
                query_normalizer=IndonesianQueryNormalizer(),
                retriever=HybridPgVectorRetriever(
                    evidence_repo=evidence_repo,
                    embedding_provider=embedder,
                ),
                reranker=LexicalOverlapReranker(),
                assessor=HybridGroundedAssessor(min_confidence_threshold=0.35),
                explainer=HybridGroundedExplainer(safety_guard=safety_guard),
                citation_validator=ProgrammaticCitationValidator(),
                model_version="hybrid-integration-test",
                min_rerank_score=0.35,
            )
            settings = Settings(ai_provider="hybrid")
            verif_service = VerificationService(
                orchestrator=orchestrator,
                verification_repo=VerificationRepository(session=session),
                settings=settings,
            )
            result = await verif_service.verify_claim(
                VerificationRequestInput(
                    text=(
                        f"Kode uji {unique_marker} cuci tangan pakai sabun mencegah penularan "
                        "diare dan infeksi."
                    ),
                    language="id",
                )
            )
            created_request_id = uuid.UUID(result.request_id)
            assert result.persisted is True
            assert result.claims[0].verdict == "SUPPORTED"
            assert result.claims[0].assessment_id is not None

            feedback_service = FeedbackService(
                feedback_repo=FeedbackRepository(session=session),
                settings=settings,
            )
            feedback_res = await feedback_service.submit_feedback(
                FeedbackRequestInput(
                    request_id=created_request_id,
                    assessment_id=uuid.UUID(result.claims[0].assessment_id),
                    is_helpful=True,
                    feedback_category="CLARITY",
                    comment="Uji integrasi PostgreSQL berjalan lancar.",
                    feedback_token=result.feedback_token,
                )
            )
            assert feedback_res.persisted is True

            # Verify duplicate feedback hits 409 DUPLICATE_FEEDBACK cleanly
            with pytest.raises(AppError) as dup_exc:
                await feedback_service.submit_feedback(
                    FeedbackRequestInput(
                        request_id=created_request_id,
                        assessment_id=uuid.UUID(result.claims[0].assessment_id),
                        is_helpful=False,
                        feedback_category="CITATIONS",
                        feedback_token=result.feedback_token,
                    )
                )
            assert dup_exc.value.status_code == 409

            # Verify private request input_text is redacted at rest in PostgreSQL
            stored_req = await session.scalar(
                select(VerificationRequest).where(VerificationRequest.id == created_request_id)
            )
            assert stored_req is not None
            assert stored_req.input_text.startswith("[redacted-private-claim:")
            assert unique_marker not in stored_req.input_text

            # Verify chunks_count stayed consistent after in-place reembed
            chunk_count = await session.scalar(
                select(func.count(EvidenceChunk.id)).where(EvidenceChunk.document_id == doc_id)
            )
            assert chunk_count == 1
    finally:
        async with session_factory() as cleanup:
            if created_request_id is not None:
                await cleanup.execute(
                    delete(VerificationRequest).where(VerificationRequest.id == created_request_id)
                )
            if created_doc_id is not None:
                await cleanup.execute(
                    delete(EvidenceDocument).where(EvidenceDocument.id == created_doc_id)
                )
            await cleanup.commit()
        await engine.dispose()
