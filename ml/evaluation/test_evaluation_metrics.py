"""Unit and benchmark tests for the VeriMed offline evaluation suite."""

from pathlib import Path

import pytest

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
