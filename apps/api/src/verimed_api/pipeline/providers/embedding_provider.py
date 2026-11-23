"""Pluggable multilingual embedding providers (offline deterministic hash & SentenceTransformer)."""

import asyncio
import hashlib
import math
import re
from typing import Any, Protocol

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


class EmbeddingProviderProtocol(Protocol):
    """Interface for dense text embedding generation."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


class DeterministicHashEmbeddingProvider:
    """Lightweight 768-d feature-hashing embedder for zero-download local development & tests."""

    def __init__(self, dimension: int = 768) -> None:
        if dimension <= 0:
            raise ValueError("Embedding dimension must be positive")
        self._dimension = dimension

    def _encode_single(self, text: str) -> list[float]:
        vec = [0.0] * self._dimension
        tokens = TOKEN_RE.findall(text.lower())
        if not tokens:
            return vec

        # Project unigrams and character 3-grams onto fixed dimensions via SHA-256
        features: list[str] = list(tokens)
        for token in tokens:
            if len(token) >= 3:
                features.extend(token[i : i + 3] for i in range(len(token) - 2))

        for feat in features:
            digest = hashlib.sha256(feat.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self._dimension
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            vec[idx] += sign

        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0.0:
            return vec
        return [round(v / norm, 6) for v in vec]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Encode document passages into unit-normalized vectors."""
        return [self._encode_single(text) for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        """Encode search query into a unit-normalized vector."""
        return self._encode_single(text)


class SentenceTransformerEmbeddingProvider:
    """Lazy-loaded multilingual SentenceTransformer provider (intfloat/multilingual-e5-base)."""

    def __init__(self, model_name: str = "intfloat/multilingual-e5-base") -> None:
        self._model_name = model_name
        self._model: Any = None

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "sentence-transformers is not installed. Install optional ML extras with "
                    '`pip install -e ".[ml]"` or set EMBEDDING_BACKEND=hash.'
                ) from exc
            self._model = SentenceTransformer(self._model_name)
        return self._model

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Encode passages using E5 `passage:` prefix without blocking event loop."""
        if not texts:
            return []
        model = self._get_model()
        prefixed = [f"passage: {t}" for t in texts]
        vectors = await asyncio.to_thread(model.encode, prefixed, normalize_embeddings=True)
        return [vec.tolist() for vec in vectors]

    async def embed_query(self, text: str) -> list[float]:
        """Encode query using E5 `query:` prefix without blocking event loop."""
        model = self._get_model()
        vector = await asyncio.to_thread(model.encode, f"query: {text}", normalize_embeddings=True)
        return list(vector.tolist())
