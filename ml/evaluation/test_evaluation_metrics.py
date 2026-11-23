"""Unit and benchmark tests for the VeriMed offline evaluation suite and curated corpus."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from verimed_api.pipeline.providers.embedding_provider import (
    DeterministicHashEmbeddingProvider,
)
from verimed_api.services.ingestion_service import (
    IngestionDocumentInput,
    IngestionService,
)

from ml.evaluation.metrics import (
    compute_abstention_precision,
    compute_citation_fidelity,
    compute_macro_f1,
    compute_mrr,
    compute_recall_at_k,
)
from ml.evaluation.run_evaluation import run_benchmark


def test_retrieval_and_classification_metrics() -> None:
    """Metric helpers compute expected Recall@K, MRR, Macro-F1, and abstention precision."""
    assert compute_recall_at_k(["a", "b", "c"], {"b"}, k=2) == 1.0
    assert compute_recall_at_k(["a", "b", "c"], {"c"}, k=2) == 0.0
    assert compute_mrr(["a", "b", "c"], {"b"}) == 0.5

    y_true = ["SUPPORTED", "CONTRADICTED", "MIXED_EVIDENCE", "INSUFFICIENT_EVIDENCE"]
    y_pred = ["SUPPORTED", "CONTRADICTED", "MIXED_EVIDENCE", "INSUFFICIENT_EVIDENCE"]
    labels = ("SUPPORTED", "CONTRADICTED", "MIXED_EVIDENCE", "INSUFFICIENT_EVIDENCE")
    assert compute_macro_f1(y_true, y_pred, labels) == 1.0
    assert compute_abstention_precision(y_true, y_pred) == 1.0
    assert compute_citation_fidelity([True, True, False, True]) == 0.75


@pytest.mark.asyncio
async def test_offline_benchmark_achieves_perfect_citation_fidelity() -> None:
    """Offline benchmark executes cleanly and achieves 100% citation validity."""
    root = Path(__file__).resolve().parents[2]
    report = await run_benchmark(
        corpus_path=root / "ml" / "data" / "synthetic_seed_evidence.json",
        benchmark_path=root / "ml" / "data" / "benchmark_claims.json",
    )
    assert report.total_cases == 7
    assert report.in_corpus_cases == 5
    assert report.recall_at_5 >= 0.8
    assert report.mrr >= 0.6
    assert report.abstention_precision >= 0.8
    assert report.citation_fidelity == 1.0


@pytest.mark.asyncio
async def test_curated_public_health_corpus_ingestion_and_benchmark() -> None:
    """Curated Kemenkes/WHO/BPOM corpus passes SSRF checks and achieves high benchmark accuracy."""
    root = Path(__file__).resolve().parents[2]
    curated_path = root / "ml" / "data" / "curated_public_health_corpus.json"
    items = json.loads(curated_path.read_text(encoding="utf-8"))
    assert len(items) >= 5

    class _StubRepo:
        async def upsert_document_with_chunks(self, record: object) -> tuple[str, bool]:
            del record
            return "doc-id", True

    service = IngestionService(
        evidence_repo=_StubRepo(),  # type: ignore[arg-type]
        embedding_provider=DeterministicHashEmbeddingProvider(),
    )

    for entry in items:
        assert entry["is_synthetic_demo"] is False
        doc = IngestionDocumentInput(
            source_name=entry["source_name"],
            source_url=entry["source_url"],
            title=entry["title"],
            authors=entry.get("authors"),
            language_code=entry.get("language_code", "id"),
            source_type=entry["source_type"],
            body_text=entry["body_text"],
            is_synthetic_demo=False,
        )
        _doc_id, created = await service.ingest_document(doc)
        assert created is True

    report = await run_benchmark(
        corpus_path=curated_path,
        benchmark_path=root / "ml" / "data" / "curated_benchmark_claims.json",
    )
    assert report.recall_at_5 == 1.0
    assert report.mrr == 1.0
    assert report.macro_f1 >= 0.9
    assert report.abstention_precision == 1.0
    assert report.citation_fidelity == 1.0
