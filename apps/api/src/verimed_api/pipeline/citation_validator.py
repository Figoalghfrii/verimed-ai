"""Programmatic citation validation ensuring zero fabricated references."""

import re

from verimed_api.pipeline.interfaces import (
    CitationEntry,
    ExplanationDraft,
    RetrievedChunkCandidate,
)

CITATION_MARKER_RE = re.compile(r"(\[\d+\])")


class ProgrammaticCitationValidator:
    """Validates that all citation markers in an explanation map to retrieved chunks."""

    def validate(
        self,
        draft: ExplanationDraft,
        evidence: list[RetrievedChunkCandidate],
        *,
        allow_empty_on_abstention: bool = True,
    ) -> tuple[bool, ExplanationDraft]:
        """Verify every [n] marker against provided retrieved evidence."""
        valid_by_key: dict[str, CitationEntry] = {
            entry.citation_key: entry for entry in draft.citations
        }
        evidence_ids = {chunk.chunk_id for chunk in evidence}

        # Keep only citations whose underlying chunk_id actually exists in retrieved evidence
        verified_entries: dict[str, CitationEntry] = {
            key: entry
            for key, entry in valid_by_key.items()
            if entry.chunk.chunk_id in evidence_ids
        }

        referenced_keys = set(CITATION_MARKER_RE.findall(draft.explanation))
        if evidence and not referenced_keys and not allow_empty_on_abstention:
            return False, ExplanationDraft(explanation=draft.explanation, citations=[])

        if not referenced_keys:
            return True, ExplanationDraft(explanation=draft.explanation, citations=[])

        all_markers_valid = referenced_keys.issubset(set(verified_entries.keys()))

        if all_markers_valid:
            ordered = [
                verified_entries[key]
                for key in sorted(
                    referenced_keys & set(verified_entries.keys()),
                    key=lambda k: int(k.strip("[]")),
                )
            ]
            return True, ExplanationDraft(explanation=draft.explanation, citations=ordered)

        # Strip unverified citation markers so no hallucinated citation reaches the user
        sanitized_explanation = CITATION_MARKER_RE.sub(
            lambda m: m.group(1) if m.group(1) in verified_entries else "",
            draft.explanation,
        )
        sanitized_explanation = re.sub(r"\s{2,}", " ", sanitized_explanation).strip()
        remaining_keys = set(CITATION_MARKER_RE.findall(sanitized_explanation))
        ordered = [
            verified_entries[key]
            for key in sorted(
                remaining_keys & set(verified_entries.keys()),
                key=lambda k: int(k.strip("[]")),
            )
        ]
        return False, ExplanationDraft(explanation=sanitized_explanation, citations=ordered)
