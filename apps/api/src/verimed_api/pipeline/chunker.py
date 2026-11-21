"""Deterministic document chunking and content hashing for evidence ingestion."""

import hashlib
import re
from dataclasses import dataclass

SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True, slots=True)
class TextChunk:
    """Single passage chunk produced from an evidence document."""

    chunk_index: int
    chunk_text: str
    token_count: int


def compute_content_hash(text: str) -> str:
    """Return stable SHA-256 hex digest for normalized document text."""
    normalized = re.sub(r"\s+", " ", text).strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


class DocumentChunker:
    """Splits long evidence texts into overlapping word-bounded passage chunks."""

    def __init__(self, max_words: int = 120, overlap_words: int = 24) -> None:
        if max_words <= 0:
            raise ValueError("max_words must be positive")
        if overlap_words < 0 or overlap_words >= max_words:
            raise ValueError("overlap_words must be >= 0 and < max_words")
        self._max_words = max_words
        self._overlap_words = overlap_words

    def chunk_text(self, text: str) -> list[TextChunk]:
        """Segment raw text into ordered TextChunk objects preserving sentences where possible."""
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return []

        sentences = [s.strip() for s in SENTENCE_BOUNDARY_RE.split(cleaned) if s.strip()]
        chunks: list[TextChunk] = []
        current_words: list[str] = []

        for sentence in sentences:
            sentence_words = sentence.split()
            if len(sentence_words) > self._max_words:
                if current_words:
                    chunks.append(
                        TextChunk(
                            chunk_index=len(chunks),
                            chunk_text=" ".join(current_words),
                            token_count=len(current_words),
                        )
                    )
                    current_words = []
                step = self._max_words - self._overlap_words
                for start in range(0, len(sentence_words), step):
                    window = sentence_words[start : start + self._max_words]
                    if not window:
                        break
                    chunks.append(
                        TextChunk(
                            chunk_index=len(chunks),
                            chunk_text=" ".join(window),
                            token_count=len(window),
                        )
                    )
                    if start + self._max_words >= len(sentence_words):
                        break
                continue

            if len(current_words) + len(sentence_words) > self._max_words and current_words:
                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        chunk_text=" ".join(current_words),
                        token_count=len(current_words),
                    )
                )
                overlap = current_words[-self._overlap_words :] if self._overlap_words > 0 else []
                current_words = [*overlap, *sentence_words]
            else:
                current_words.extend(sentence_words)

        if current_words:
            chunks.append(
                TextChunk(
                    chunk_index=len(chunks),
                    chunk_text=" ".join(current_words),
                    token_count=len(current_words),
                )
            )

        return chunks
