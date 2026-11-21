"""Pure metric functions for VeriMed offline pipeline evaluation."""

from collections.abc import Sequence
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvaluationReport:
    """Aggregated offline benchmark metrics across retrieval, stance, and citations."""

    total_cases: int
    in_corpus_cases: int
    recall_at_5: float
    recall_at_10: float
    mrr: float
    macro_f1: float
    abstention_precision: float
    citation_fidelity: float

    def to_dict(self) -> dict[str, int | float]:
        """Serialize report into a JSON-compatible dictionary."""
        return asdict(self)


def compute_recall_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Compute Recall@K for a single query. Returns 1.0 if any relevant doc is in top-K."""
    if not relevant_ids or k <= 0:
        return 0.0
    top_k = set(retrieved_ids[:k])
    hits = len(top_k & relevant_ids)
    return hits / len(relevant_ids)


def compute_mrr(
    retrieved_ids: Sequence[str],
    relevant_ids: set[str],
) -> float:
    """Compute Mean Reciprocal Rank (1 / rank of first relevant hit) for one query."""
    if not relevant_ids:
        return 0.0
    for idx, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / idx
    return 0.0


def compute_macro_f1(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str],
) -> float:
    """Compute unweighted Macro-F1 across the specified verdict labels."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have equal length.")
    if not labels:
        return 0.0

    f1_scores: list[float] = []
    for label in labels:
        tp = sum(
            1 for t, p in zip(y_true, y_pred, strict=True) if t == label and p == label
        )
        fp = sum(
            1 for t, p in zip(y_true, y_pred, strict=True) if t != label and p == label
        )
        fn = sum(
            1 for t, p in zip(y_true, y_pred, strict=True) if t == label and p != label
        )

        denom = (2 * tp) + fp + fn
        f1 = (2 * tp) / denom if denom > 0 else 0.0
        f1_scores.append(f1)

    return sum(f1_scores) / len(f1_scores)


def compute_abstention_precision(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    abstain_label: str = "INSUFFICIENT_EVIDENCE",
) -> float:
    """Compute precision when the pipeline predicts abstention (INSUFFICIENT_EVIDENCE)."""
    predicted_abstentions = [
        (t, p) for t, p in zip(y_true, y_pred, strict=True) if p == abstain_label
    ]
    if not predicted_abstentions:
        return 1.0 if abstain_label not in y_true else 0.0

    true_abstentions = sum(1 for t, _p in predicted_abstentions if t == abstain_label)
    return true_abstentions / len(predicted_abstentions)


def compute_citation_fidelity(valid_flags: Sequence[bool]) -> float:
    """Compute fraction of evaluated claims passing programmatic citation validation."""
    if not valid_flags:
        return 0.0
    return sum(1 for flag in valid_flags if flag) / len(valid_flags)
