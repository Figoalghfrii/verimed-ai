"""Deterministic rule-based health claim extractor for Phase 2 MVP."""

import re

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
MAX_CLAIMS_PER_REQUEST = 5


class DeterministicClaimExtractor:
    """Decomposes user text into bounded, atomic candidate health claims."""

    async def extract_claims(self, text: str) -> list[str]:
        """Split compound text into up to MAX_CLAIMS_PER_REQUEST atomic claims."""
        raw_segments = [seg.strip() for seg in SENTENCE_SPLIT_RE.split(text) if seg.strip()]
        claims = [seg for seg in raw_segments if len(seg) >= 10]
        if not claims and text.strip():
            claims = [text.strip()]
        return claims[:MAX_CLAIMS_PER_REQUEST]
