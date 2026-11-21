"""Reproducible offline evaluation runner for VeriMed retrieval, stance, and citations."""

import argparse
import asyncio
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
API_SRC_DIR = ROOT_DIR / "apps" / "api" / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(API_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(API_SRC_DIR))

from verimed_api.pipeline.chunker import DocumentChunker
from verimed_api.pipeline.citation_validator import ProgrammaticCitationValidator
from verimed_api.pipeline.fusion import RankedChunkHit
from verimed_api.pipeline.providers.embedding_provider import (
    DeterministicHashEmbeddingProvider,
    EmbeddingProviderProtocol,
    SentenceTransformerEmbeddingProvider,
)
from verimed_api.pipeline.providers.hybrid_grounded_provider import (
    HybridGroundedAssessor,
    HybridGroundedExplainer,
)
from verimed_api.pipeline.query_normalizer import IndonesianQueryNormalizer
from verimed_api.pipeline.reranker import (
    CrossEncoderReranker,
    LexicalOverlapReranker,
)
from verimed_api.pipeline.retriever import HybridPgVectorRetriever
from verimed_api.pipeline.safety_guard import SafetyGuard

from ml.evaluation.metrics import (
    EvaluationReport,
    compute_abstention_precision,
    compute_citation_fidelity,
    compute_macro_f1,
    compute_mrr,
    compute_recall_at_k,
)

VERDICT_LABELS = (
    "SUPPORTED",
    "CONTRADICTED",
    "MIXED_EVIDENCE",
    "INSUFFICIENT_EVIDENCE",
)
TOKEN_RE = re.compile(r"[a-z0-9]{2,}", re.IGNORECASE)


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=True))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _lexical_overlap(query: str, text: str) -> float:
    q_tokens = set(TOKEN_RE.findall(query.lower()))
    if not q_tokens:
        return 0.0
    t_tokens = set(TOKEN_RE.findall(text.lower()))
    return len(q_tokens & t_tokens) / len(q_tokens)


class _InMemoryEvidenceSearchRepo:
    """In-memory repository satisfying EvidenceSearchRepositoryProtocol for offline eval."""

    def __init__(self, indexed_chunks: list[dict[str, object]]) -> None:
        self._chunks = indexed_chunks

    def _to_ranked_hit(self, chunk: dict[str, object], score: float) -> RankedChunkHit:
        pub_raw = chunk.get("publication_date")
        pub_date = date.fromisoformat(str(pub_raw)) if pub_raw else None
        return RankedChunkHit(
            chunk_id=str(chunk["chunk_id"]),
            source_name=str(chunk["source_name"]),
            source_type=str(chunk["source_type"]),
            title=str(chunk["title"]),
            source_url=str(chunk["source_url"]),
            publication_date=pub_date,
            chunk_text=str(chunk["chunk_text"]),
            raw_score=score,
            is_synthetic_demo=bool(chunk["is_synthetic_demo"]),
        )

    async def search_lexical(
        self, query_text: str, limit: int = 20
    ) -> list[RankedChunkHit]:
        scored = [
            (c, _lexical_overlap(query_text, f"{c['title']} {c['chunk_text']}"))
            for c in self._chunks
        ]
        scored = [pair for pair in scored if pair[1] > 0.0]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [self._to_ranked_hit(c, score) for c, score in scored[:limit]]

    async def search_vector(
        self, query_embedding: list[float], limit: int = 20
    ) -> list[RankedChunkHit]:
        scored = [
            (c, _cosine_similarity(query_embedding, c["embedding"]))  # type: ignore[arg-type]
            for c in self._chunks
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [self._to_ranked_hit(c, max(0.0, score)) for c, score in scored[:limit]]


async def run_benchmark(
    *,
    corpus_path: Path,
    benchmark_path: Path,
    embedding_backend: str = "hash",
    reranker_backend: str = "lexical",
    min_rerank_score: float = 0.35,
) -> EvaluationReport:
    """Execute end-to-end offline evaluation on a JSON corpus and claim benchmark."""
    raw_corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    raw_benchmarks = json.loads(benchmark_path.read_text(encoding="utf-8"))

    embedder: EmbeddingProviderProtocol = (
        SentenceTransformerEmbeddingProvider()
        if embedding_backend == "sentence_transformers"
        else DeterministicHashEmbeddingProvider()
    )
    reranker = (
        CrossEncoderReranker()
        if reranker_backend == "cross_encoder"
        else LexicalOverlapReranker()
    )
    chunker = DocumentChunker()
    normalizer = IndonesianQueryNormalizer()
    safety_guard = SafetyGuard()
    assessor = HybridGroundedAssessor(min_confidence_threshold=min_rerank_score)
    explainer = HybridGroundedExplainer(safety_guard=safety_guard)
    citation_validator = ProgrammaticCitationValidator()

    indexed_chunks: list[dict[str, object]] = []
    for doc_idx, doc in enumerate(raw_corpus, start=1):
        chunks = chunker.chunk_text(doc["body_text"])
        embeddings = await embedder.embed_documents([c.chunk_text for c in chunks])
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            indexed_chunks.append(
                {
                    "chunk_id": f"eval-doc-{doc_idx}-chunk-{chunk.chunk_index}",
                    "source_url": doc["source_url"],
                    "source_name": doc["source_name"],
                    "source_type": doc["source_type"],
                    "title": doc["title"],
                    "publication_date": doc.get("publication_date"),
                    "is_synthetic_demo": bool(doc.get("is_synthetic_demo", True)),
                    "chunk_text": chunk.chunk_text,
                    "embedding": embedding,
                }
            )

    repo = _InMemoryEvidenceSearchRepo(indexed_chunks)
    retriever = HybridPgVectorRetriever(evidence_repo=repo, embedding_provider=embedder)

    recall_5_scores: list[float] = []
    recall_10_scores: list[float] = []
    mrr_scores: list[float] = []
    y_true: list[str] = []
    y_pred: list[str] = []
    citation_valid_flags: list[bool] = []

    for item in raw_benchmarks:
        claim_text = item["claim_text"]
        expected_verdict = item["expected_verdict"]
        relevant_urls = set(item.get("relevant_source_urls", []))

        normalized_query = await normalizer.normalize(claim_text)
        candidates = await retriever.retrieve(
            claim_text=claim_text,
            normalized_query=normalized_query,
            top_k=10,
        )

        deduped_urls = list(dict.fromkeys(c.source_url for c in candidates))
        if relevant_urls:
            recall_5_scores.append(
                compute_recall_at_k(deduped_urls, relevant_urls, k=5)
            )
            recall_10_scores.append(
                compute_recall_at_k(deduped_urls, relevant_urls, k=10)
            )
            mrr_scores.append(compute_mrr(deduped_urls, relevant_urls))

        reranked = await reranker.rerank(
            claim_text=claim_text,
            candidates=candidates,
            min_score=min_rerank_score,
        )
        assessment = await assessor.assess(claim_text=claim_text, evidence=reranked)
        draft = await explainer.explain(
            claim_text=claim_text,
            assessment=assessment,
            evidence=reranked,
        )
        citations_valid, _validated = citation_validator.validate(
            draft=draft, evidence=reranked
        )

        y_true.append(expected_verdict)
        y_pred.append(assessment.verdict)
        citation_valid_flags.append(citations_valid)

    return EvaluationReport(
        total_cases=len(raw_benchmarks),
        in_corpus_cases=len(recall_5_scores),
        recall_at_5=round(sum(recall_5_scores) / len(recall_5_scores), 4)
        if recall_5_scores
        else 0.0,
        recall_at_10=round(sum(recall_10_scores) / len(recall_10_scores), 4)
        if recall_10_scores
        else 0.0,
        mrr=round(sum(mrr_scores) / len(mrr_scores), 4) if mrr_scores else 0.0,
        macro_f1=round(compute_macro_f1(y_true, y_pred, VERDICT_LABELS), 4),
        abstention_precision=round(compute_abstention_precision(y_true, y_pred), 4),
        citation_fidelity=round(compute_citation_fidelity(citation_valid_flags), 4),
    )


def main() -> int:
    default_corpus = ROOT_DIR / "ml" / "data" / "synthetic_seed_evidence.json"
    default_benchmark = ROOT_DIR / "ml" / "data" / "benchmark_claims.json"

    parser = argparse.ArgumentParser(
        description="Run VeriMed offline evaluation suite."
    )
    parser.add_argument("--corpus", type=Path, default=default_corpus)
    parser.add_argument("--benchmark", type=Path, default=default_benchmark)
    parser.add_argument("--embedding-backend", default="hash")
    parser.add_argument("--reranker-backend", default="lexical")
    parser.add_argument("--min-score", type=float, default=0.35)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    report = asyncio.run(
        run_benchmark(
            corpus_path=args.corpus,
            benchmark_path=args.benchmark,
            embedding_backend=args.embedding_backend,
            reranker_backend=args.reranker_backend,
            min_rerank_score=args.min_score,
        )
    )
    payload = json.dumps(report.to_dict(), indent=2)
    print(payload)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
