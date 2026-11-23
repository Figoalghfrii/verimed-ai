"""Quota, circuit-breaker, and groundedness guards for external LLM providers."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from verimed_api.core.config import Settings, get_settings
from verimed_api.pipeline.interfaces import CitationEntry, RetrievedChunkCandidate

URL_OR_DOI_RE = re.compile(
    r"(https?://\S+|10\.\d{4,9}/[-._;()/:A-Za-z0-9]+|doi\.org/\S+)",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
PROMPT_LEAKAGE_MARKERS = (
    "<untrusted_evidence>",
    "</untrusted_evidence>",
    "ignore previous instructions",
    "system prompt",
)


@dataclass
class _GuardState:
    utc_date: str
    daily_calls: int = 0
    consecutive_failures: int = 0
    circuit_open_until: float = 0.0


class LLMQuotaAndCircuitGuard:
    """Bounded daily call budget and consecutive-failure circuit breaker for external LLMs."""

    def __init__(
        self,
        *,
        daily_budget: int = 500,
        failure_threshold: int = 5,
        cooldown_seconds: int = 60,
    ) -> None:
        self._daily_budget = max(0, daily_budget)
        self._failure_threshold = max(1, failure_threshold)
        self._cooldown_seconds = max(1, cooldown_seconds)
        self._state = _GuardState(utc_date=self._today_utc())

    @staticmethod
    def _today_utc() -> str:
        return datetime.now(tz=UTC).date().isoformat()

    def _roll_day_if_needed(self) -> None:
        today = self._today_utc()
        if self._state.utc_date != today:
            self._state.utc_date = today
            self._state.daily_calls = 0

    def try_acquire(self) -> tuple[bool, str | None]:
        """Reserve one external LLM call slot if within budget and circuit is closed."""
        self._roll_day_if_needed()
        now = time.monotonic()
        if self._state.circuit_open_until > now:
            return False, "circuit_open"
        if self._daily_budget == 0 or self._state.daily_calls >= self._daily_budget:
            return False, "daily_budget_exceeded"
        self._state.daily_calls += 1
        return True, None

    def record_success(self) -> None:
        """Reset consecutive failure count after a valid upstream LLM call."""
        self._state.consecutive_failures = 0
        self._state.circuit_open_until = 0.0

    def record_failure(self) -> bool:
        """Increment failure counter and open circuit on reaching threshold."""
        self._state.consecutive_failures += 1
        if self._state.consecutive_failures >= self._failure_threshold:
            self._state.circuit_open_until = time.monotonic() + self._cooldown_seconds
            return True
        return False

    def reset(self) -> None:
        """Reset counters and circuit breaker state (for deterministic tests)."""
        self._state = _GuardState(utc_date=self._today_utc())


_SHARED_LLM_GUARD: LLMQuotaAndCircuitGuard | None = None


def get_llm_guard(settings: Settings | None = None) -> LLMQuotaAndCircuitGuard:
    """Return shared LLM quota and circuit-breaker guard for the running API process."""
    global _SHARED_LLM_GUARD
    cfg = settings or get_settings()
    if _SHARED_LLM_GUARD is None:
        _SHARED_LLM_GUARD = LLMQuotaAndCircuitGuard(
            daily_budget=cfg.llm_daily_call_budget,
            failure_threshold=cfg.llm_circuit_breaker_threshold,
            cooldown_seconds=cfg.llm_circuit_breaker_cooldown_seconds,
        )
    return _SHARED_LLM_GUARD


def reset_shared_llm_guard() -> None:
    """Reset the shared LLM guard singleton."""
    global _SHARED_LLM_GUARD
    _SHARED_LLM_GUARD = None


def verify_llm_explanation_groundedness(
    *,
    explanation: str,
    claim_text: str,
    cited_entries: list[CitationEntry],
    evidence: list[RetrievedChunkCandidate],
    citation_pattern: re.Pattern[str],
) -> tuple[bool, str | None]:
    """Ensure LLM prose only references grounded citations, known URLs/DOIs, and evidence years."""
    cleaned = explanation.strip()
    if not cleaned:
        return False, "empty_explanation"

    lowered = cleaned.lower()
    if any(marker in lowered for marker in PROMPT_LEAKAGE_MARKERS):
        return False, "prompt_leakage_detected"

    referenced_keys = set(citation_pattern.findall(cleaned))
    if evidence and not referenced_keys:
        return False, "missing_citation_markers"

    available_keys = {entry.citation_key for entry in cited_entries}
    if not referenced_keys.issubset(available_keys):
        return False, "invalid_citation_marker_key"

    allowed_corpus_blob = " ".join(
        [
            claim_text,
            *(chunk.title for chunk in evidence),
            *(chunk.source_name for chunk in evidence),
            *(chunk.source_url for chunk in evidence),
            *(chunk.chunk_text for chunk in evidence),
            *(
                chunk.publication_date.isoformat()
                for chunk in evidence
                if chunk.publication_date is not None
            ),
        ]
    ).lower()

    for match in URL_OR_DOI_RE.findall(cleaned):
        normalized = match.rstrip(".,);:]")
        if normalized.lower() not in allowed_corpus_blob:
            return False, "ungrounded_url_or_doi"

    for year in YEAR_RE.findall(cleaned):
        if year not in allowed_corpus_blob:
            return False, "ungrounded_year_reference"

    return True, None
