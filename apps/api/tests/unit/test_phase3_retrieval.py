"""Unit tests for Phase 3 chunking, hybrid RRF fusion, reranking, and configurable LLM."""

import json
import math
from datetime import date

import httpx
import pytest

from verimed_api.pipeline.chunker import DocumentChunker, compute_content_hash
from verimed_api.pipeline.fusion import RankedChunkHit, fuse_ranked_lists
from verimed_api.pipeline.interfaces import RetrievedChunkCandidate
from verimed_api.pipeline.providers.configurable_provider import (
    ConfigurableLLMAssessorExplainer,
)
from verimed_api.pipeline.providers.embedding_provider import (
    DeterministicHashEmbeddingProvider,
)
from verimed_api.pipeline.providers.hybrid_grounded_provider import (
    HybridGroundedAssessor,
    HybridGroundedExplainer,
)
from verimed_api.pipeline.reranker import LexicalOverlapReranker
from verimed_api.pipeline.retriever import HybridPgVectorRetriever
from verimed_api.pipeline.safety_guard import SafetyGuard
from verimed_api.repositories.evidence_repo import build_safe_or_query
from verimed_api.services.ingestion_service import IngestionDocumentInput, IngestionService


def test_document_chunker_splits_with_overlap_and_stable_hash() -> None:
    chunker = DocumentChunker(max_words=15, overlap_words=3)
    text = (
        "Kalimat pertama membahas cuci tangan pakai sabun secara rutin setiap hari. "
        "Kalimat kedua menjelaskan bagaimana sabun melarutkan lapisan lemak patogen di kulit. "
        "Kalimat ketiga menekankan pentingnya durasi mencuci tangan minimal dua puluh detik."
    )
    chunks = chunker.chunk_text(text)
    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0
    assert compute_content_hash(text) == compute_content_hash(f"  {text}  ")


def test_rrf_fusion_combines_and_ranks_overlapping_hits_higher() -> None:
    hit_a_lex = RankedChunkHit(
        chunk_id="chunk-a",
        source_name="Demo",
        source_type="DEMO",
        title="Title A",
        source_url="https://demo.verimed.local/a",
        publication_date=date(2025, 1, 1),
        chunk_text="Antibiotik tidak efektif untuk flu virus.",
        raw_score=0.9,
        is_synthetic_demo=True,
    )
    hit_b_lex = RankedChunkHit(
        chunk_id="chunk-b",
        source_name="Demo",
        source_type="DEMO",
        title="Title B",
        source_url="https://demo.verimed.local/b",
        publication_date=date(2025, 1, 1),
        chunk_text="Cuci tangan mencegah diare.",
        raw_score=0.4,
        is_synthetic_demo=True,
    )
    hit_a_vec = RankedChunkHit(
        chunk_id="chunk-a",
        source_name="Demo",
        source_type="DEMO",
        title="Title A",
        source_url="https://demo.verimed.local/a",
        publication_date=date(2025, 1, 1),
        chunk_text="Antibiotik tidak efektif untuk flu virus.",
        raw_score=0.88,
        is_synthetic_demo=True,
    )

    fused = fuse_ranked_lists([hit_a_lex, hit_b_lex], [hit_a_vec], top_k=5)
    assert fused[0].chunk_id == "chunk-a"
    assert fused[0].hybrid_score > fused[1].hybrid_score


async def test_deterministic_hash_embedder_produces_unit_normalized_768d_vectors() -> None:
    embedder = DeterministicHashEmbeddingProvider(dimension=768)
    vectors = await embedder.embed_documents(["Cuci tangan pakai sabun mencegah infeksi."])
    assert len(vectors) == 1
    assert len(vectors[0]) == 768
    norm = math.sqrt(sum(v * v for v in vectors[0]))
    assert math.isclose(norm, 1.0, rel_tol=1e-3)


async def test_lexical_overlap_reranker_filters_irrelevant_candidates() -> None:
    reranker = LexicalOverlapReranker()
    relevant = RetrievedChunkCandidate(
        chunk_id="1",
        source_name="Demo",
        source_type="DEMO",
        title="Antibiotik dan Infeksi Virus",
        source_url="https://demo.verimed.local/1",
        publication_date=None,
        chunk_text="Antibiotik tidak efektif menyembuhkan flu atau pilek akibat virus.",
        lexical_score=0.8,
        vector_score=0.8,
        hybrid_score=0.85,
        rerank_score=0.85,
        stance="CONTEXTUAL",
        is_synthetic_demo=True,
    )
    irrelevant = RetrievedChunkCandidate(
        chunk_id="2",
        source_name="Demo",
        source_type="DEMO",
        title="Kesehatan Gigi",
        source_url="https://demo.verimed.local/2",
        publication_date=None,
        chunk_text="Menyikat gigi dua kali sehari menjaga kebersihan mulut.",
        lexical_score=0.1,
        vector_score=0.1,
        hybrid_score=0.1,
        rerank_score=0.1,
        stance="CONTEXTUAL",
        is_synthetic_demo=True,
    )

    ranked = await reranker.rerank(
        "Apakah antibiotik bisa menyembuhkan flu virus?",
        [irrelevant, relevant],
        min_score=0.35,
    )
    assert len(ranked) == 1
    assert ranked[0].chunk_id == "1"


async def test_hybrid_retriever_and_grounded_assessor_abstention() -> None:
    class _StubSearchRepo:
        async def search_lexical(self, query_text: str, limit: int = 20) -> list[RankedChunkHit]:
            del query_text, limit
            return [
                RankedChunkHit(
                    chunk_id="c1",
                    source_name="Demo",
                    source_type="DEMO",
                    title="Antibiotik",
                    source_url="https://demo.verimed.local/abx",
                    publication_date=None,
                    chunk_text="Antibiotik tidak efektif menyembuhkan flu karena virus.",
                    raw_score=0.85,
                    is_synthetic_demo=True,
                )
            ]

        async def search_vector(
            self, query_embedding: list[float], limit: int = 20
        ) -> list[RankedChunkHit]:
            del query_embedding, limit
            return []

    retriever = HybridPgVectorRetriever(
        evidence_repo=_StubSearchRepo(),
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )
    hits = await retriever.retrieve("Antibiotik menyembuhkan flu", "antibiotik flu")
    assert len(hits) == 1

    assessor = HybridGroundedAssessor(min_confidence_threshold=0.35)
    outcome = await assessor.assess("Antibiotik menyembuhkan flu", hits)
    assert outcome.verdict == "CONTRADICTED"
    assert outcome.abstained is False

    abstain_outcome = await assessor.assess("Klaim tidak berdasar", [])
    assert abstain_outcome.verdict == "INSUFFICIENT_EVIDENCE"
    assert abstain_outcome.abstained is True

    explainer = HybridGroundedExplainer(safety_guard=SafetyGuard())
    draft = await explainer.explain("Antibiotik menyembuhkan flu", outcome, hits)
    assert "[1]" in draft.explanation


async def test_configurable_llm_provider_parses_structured_json_and_guards_abstention() -> None:
    def _mock_handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        user_msg = body["messages"][1]["content"]
        assert "<untrusted_evidence" in user_msg
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "verdict": "CONTRADICTED",
                                    "confidence_score": 0.91,
                                    "abstained": False,
                                    "abstention_reason": None,
                                    "explanation": (
                                        "Bukti menunjukkan antibiotik tidak efektif "
                                        "melawan virus [1]."
                                    ),
                                    "uncertainty_notes": (
                                        "Penilaian terbatas pada sumber terindeks."
                                    ),
                                }
                            )
                        }
                    }
                ]
            },
        )

    provider = ConfigurableLLMAssessorExplainer(
        safety_guard=SafetyGuard(),
        base_url="https://llm.example.test/v1",
        api_key="test-key-not-real",
        model_name="test-model",
        transport=httpx.MockTransport(_mock_handler),
    )

    candidate = RetrievedChunkCandidate(
        chunk_id="c-1",
        source_name="Demo",
        source_type="DEMO",
        title="Antibiotik",
        source_url="https://demo.verimed.local/abx",
        publication_date=None,
        chunk_text="Antibiotik tidak efektif untuk virus.",
        lexical_score=0.9,
        vector_score=0.9,
        hybrid_score=0.9,
        rerank_score=0.9,
        stance="CONTRADICTING",
        is_synthetic_demo=True,
    )

    assessment = await provider.assess("Antibiotik menyembuhkan flu", [candidate])
    assert assessment.verdict == "CONTRADICTED"
    draft = await provider.explain("Antibiotik menyembuhkan flu", assessment, [candidate])
    assert "[1]" in draft.explanation


async def test_ingestion_service_rejects_unsafe_non_demo_urls() -> None:
    class _DummyRepo:
        async def upsert_document_with_chunks(self, record: object) -> tuple[object, bool]:
            raise AssertionError("Should not reach repository for unsafe URL")

    service = IngestionService(
        evidence_repo=_DummyRepo(),  # type: ignore[arg-type]
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )

    with pytest.raises(ValueError, match="SSRF guard"):
        await service.ingest_document(
            IngestionDocumentInput(
                source_name="Bad Source",
                source_url="http://127.0.0.1/internal",
                title="Unsafe",
                body_text="Konten uji keamanan SSRF untuk memastikan URL lokal ditolak.",
                source_type="TEST",
                is_synthetic_demo=False,
            )
        )


def test_build_safe_or_query_strips_special_operators() -> None:
    assert (
        build_safe_or_query("cuci tangan | sabun: !@# diare") == "cuci OR tangan OR sabun OR diare"
    )


async def test_configurable_llm_provider_supports_gemini_fences_and_untrusted_claim() -> None:
    def _mock_gemini_handler(request: httpx.Request) -> httpx.Response:
        assert (
            str(request.url)
            == "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        )
        body = json.loads(request.content.decode("utf-8"))
        user_msg = body["messages"][1]["content"]
        assert "<untrusted_claim>" in user_msg
        assert "</untrusted_claim>" in user_msg
        fenced_json = (
            "```json\n"
            + json.dumps(
                {
                    "verdict": "MIXED_EVIDENCE",
                    "confidence_score": 0.78,
                    "abstained": False,
                    "abstention_reason": None,
                    "explanation": "According to primary review [1], results vary by subgroup.",
                    "uncertainty_notes": None,
                }
            )
            + "\n```"
        )
        return httpx.Response(200, json={"choices": [{"message": {"content": fenced_json}}]})

    provider = ConfigurableLLMAssessorExplainer(
        safety_guard=SafetyGuard(),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions/",
        api_key="test-gemini-key",
        model_name="gemini-2.5-flash",
        transport=httpx.MockTransport(_mock_gemini_handler),
    )

    c1 = RetrievedChunkCandidate(
        chunk_id="c-1",
        source_name="NIH ODS",
        source_type="OFFICIAL_GUIDELINE",
        title="Vitamin C",
        source_url="https://ods.od.nih.gov/factsheets/VitaminC-Consumer/",
        publication_date=None,
        chunk_text="Mixed findings on vitamin C for common cold.",
        lexical_score=0.9,
        vector_score=0.9,
        hybrid_score=0.9,
        rerank_score=0.9,
        stance="CONTEXTUAL",
        is_synthetic_demo=False,
    )
    c2 = RetrievedChunkCandidate(
        chunk_id="c-2",
        source_name="Other",
        source_type="OFFICIAL_GUIDELINE",
        title="Other context",
        source_url="https://www.who.int/other",
        publication_date=None,
        chunk_text="Additional background text.",
        lexical_score=0.5,
        vector_score=0.5,
        hybrid_score=0.5,
        rerank_score=0.5,
        stance="CONTEXTUAL",
        is_synthetic_demo=False,
    )

    assessment = await provider.assess("Vitamin C prevents colds", [c1, c2], language="en")
    assert assessment.verdict == "MIXED_EVIDENCE"
    assert len(assessment.uncertainty_notes) >= 5
    draft = await provider.explain("Vitamin C prevents colds", assessment, [c1, c2], language="en")
    assert [c.citation_key for c in draft.citations] == ["[1]"]


async def test_hybrid_grounded_bilingual_and_negated_claim_alignment() -> None:
    reranker = LexicalOverlapReranker()
    ctps_chunk = RetrievedChunkCandidate(
        chunk_id="c-ctps",
        source_name="Kementerian Kesehatan RI",
        source_type="OFFICIAL_GUIDELINE",
        title="Cuci Tangan Pakai Sabun",
        source_url="https://kemkes.go.id/id/ctps",
        publication_date=None,
        chunk_text=(
            "Cuci tangan pakai sabun terbukti efektif mencegah penularan diare dan infeksi."
        ),
        lexical_score=0.85,
        vector_score=0.82,
        hybrid_score=0.85,
        rerank_score=0.85,
        stance="CONTEXTUAL",
        is_synthetic_demo=False,
    )
    ranked_en = await reranker.rerank(
        "Washing hands with soap prevents diarrhea",
        [ctps_chunk],
        min_score=0.35,
    )
    assert len(ranked_en) == 1
    assert ranked_en[0].rerank_score >= 0.35

    assessor = HybridGroundedAssessor(min_confidence_threshold=0.35)
    abx_chunk = RetrievedChunkCandidate(
        chunk_id="c-abx",
        source_name="WHO",
        source_type="WHO_FACT_SHEET",
        title="AMR",
        source_url="https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance",
        publication_date=None,
        chunk_text="Antibiotik tidak efektif untuk mengobati flu virus biasa.",
        lexical_score=0.9,
        vector_score=0.9,
        hybrid_score=0.9,
        rerank_score=0.9,
        stance="CONTEXTUAL",
        is_synthetic_demo=False,
    )

    # Negated accurate claim agrees with refuting WHO evidence -> SUPPORTED
    negated_ok = await assessor.assess(
        "Antibiotik tidak dapat menyembuhkan flu karena virus.",
        [abx_chunk],
    )
    assert negated_ok.verdict == "SUPPORTED"

    # Negated false claim contradicting supportive evidence -> CONTRADICTED
    negated_false = await assessor.assess(
        "Cuci tangan pakai sabun tidak mencegah diare.",
        ranked_en,
    )
    assert negated_false.verdict == "CONTRADICTED"


async def test_ingestion_service_forwards_force_reembed_flag() -> None:
    calls: list[bool] = []

    class _RecordingRepo:
        async def upsert_document_with_chunks(
            self, record: object, *, force_reembed: bool = False
        ) -> tuple[object, bool]:
            del record
            calls.append(force_reembed)
            return "doc-id", False

    service = IngestionService(
        evidence_repo=_RecordingRepo(),  # type: ignore[arg-type]
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )
    await service.ingest_document(
        IngestionDocumentInput(
            source_name="WHO",
            source_url="https://www.who.int/news-room/fact-sheets/detail/measles",
            title="Measles Fact Sheet",
            body_text="Vaksin campak aman dan efektif melindungi anak.",
            source_type="WHO_FACT_SHEET",
            is_synthetic_demo=False,
        ),
        force_reembed=True,
    )
    assert calls == [True]
