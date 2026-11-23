"""Reproducible CLI script to seed curated or synthetic evidence into PostgreSQL + pgvector."""

import argparse
import asyncio
import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from verimed_api.core.config import get_settings
from verimed_api.core.database import AsyncSessionLocal
from verimed_api.core.security import is_safe_external_url
from verimed_api.pipeline.providers.embedding_provider import (
    DeterministicHashEmbeddingProvider,
    EmbeddingProviderProtocol,
    SentenceTransformerEmbeddingProvider,
)
from verimed_api.repositories.evidence_repo import EvidenceRepository
from verimed_api.services.ingestion_service import (
    IngestionDocumentInput,
    IngestionService,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "ml" / "data"


class CorpusEntrySchema(BaseModel):
    """Schema validating seeded evidence corpus JSON entries against SSRF and truncation."""

    source_name: str = Field(..., min_length=2, max_length=128)
    source_url: str = Field(..., min_length=8, max_length=2048)
    title: str = Field(..., min_length=3, max_length=500)
    authors: str | None = Field(default=None, max_length=500)
    publication_date: str | None = None
    language_code: str = Field(default="id", min_length=2, max_length=10)
    source_type: str = Field(..., min_length=2, max_length=64)
    body_text: str = Field(..., min_length=20)
    is_synthetic_demo: bool = False

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        if not is_safe_external_url(value, resolve_dns=False):
            raise ValueError(f"Unsafe or non-HTTPS corpus source_url: {value}")
        return value


CORPUS_PRESETS: dict[str, list[Path]] = {
    "synthetic": [DATA_DIR / "synthetic_seed_evidence.json"],
    "curated": [DATA_DIR / "curated_public_health_corpus.json"],
    "all": [
        DATA_DIR / "synthetic_seed_evidence.json",
        DATA_DIR / "curated_public_health_corpus.json",
    ],
}


def _build_embedder() -> EmbeddingProviderProtocol:
    settings = get_settings()
    if settings.embedding_backend == "sentence_transformers":
        return SentenceTransformerEmbeddingProvider(
            model_name=settings.embedding_model_name
        )
    return DeterministicHashEmbeddingProvider(dimension=settings.embedding_dimension)


async def seed_corpora(
    corpus_paths: list[Path], *, force_reembed: bool = False
) -> None:
    """Load JSON documents from one or more files, chunk, embed, and upsert idempotently."""
    embedder = _build_embedder()
    created_count = 0
    existing_count = 0

    async with AsyncSessionLocal() as session:
        repo = EvidenceRepository(session=session)
        service = IngestionService(evidence_repo=repo, embedding_provider=embedder)

        for corpus_path in corpus_paths:
            resolved_path = corpus_path.resolve()
            if not resolved_path.is_file():
                raise FileNotFoundError(f"Corpus file not found: {resolved_path}")
            if not resolved_path.is_relative_to(DATA_DIR.resolve()):
                print(f"[WARNING] Custom corpus path outside ml/data/: {resolved_path}")
            raw_items = json.loads(resolved_path.read_text(encoding="utf-8"))
            if not isinstance(raw_items, list):
                raise TypeError(
                    f"Corpus JSON must be a list of documents: {resolved_path}"
                )
            for raw_entry in raw_items:
                validated = CorpusEntrySchema.model_validate(raw_entry)
                pub_date = (
                    date.fromisoformat(validated.publication_date)
                    if validated.publication_date
                    else None
                )
                doc_input = IngestionDocumentInput(
                    source_name=validated.source_name,
                    source_url=validated.source_url,
                    title=validated.title,
                    authors=validated.authors,
                    publication_date=pub_date,
                    language_code=validated.language_code,
                    source_type=validated.source_type,
                    body_text=validated.body_text,
                    is_synthetic_demo=validated.is_synthetic_demo,
                )
                _doc_id, created = await service.ingest_document(
                    doc_input, force_reembed=force_reembed
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

        stats = await service.get_stats()
        print(
            f"Seed complete: created={created_count}, "
            f"{'reembedded_existing' if force_reembed else 'skipped_existing'}={existing_count}, "
            f"total_documents={stats.documents_count}, "
            f"curated_documents={stats.documents_count - stats.synthetic_documents_count}, "
            f"synthetic_documents={stats.synthetic_documents_count}, "
            f"total_chunks={stats.chunks_count}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed VeriMed synthetic or curated public-health corpus into PostgreSQL."
    )
    parser.add_argument(
        "--preset",
        choices=tuple(CORPUS_PRESETS.keys()),
        default="curated",
        help="Built-in corpus preset to ingest (default: curated).",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=None,
        help="Optional custom JSON corpus file path (overrides --preset).",
    )
    parser.add_argument(
        "--force-reembed",
        action="store_true",
        help="Regenerate and overwrite chunk embeddings/search vectors for existing documents.",
    )
    args = parser.parse_args()
    paths = [args.corpus] if args.corpus is not None else CORPUS_PRESETS[args.preset]
    asyncio.run(seed_corpora(paths, force_reembed=args.force_reembed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
