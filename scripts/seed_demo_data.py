"""Reproducible CLI script to seed curated or synthetic evidence into PostgreSQL + pgvector."""

import argparse
import asyncio
import json
from datetime import date
from pathlib import Path

from verimed_api.core.config import get_settings
from verimed_api.core.database import AsyncSessionLocal
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

DATA_DIR = Path(__file__).resolve().parents[1] / "ml" / "data"
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


async def seed_corpora(corpus_paths: list[Path]) -> None:
    """Load JSON documents from one or more files, chunk, embed, and upsert idempotently."""
    embedder = _build_embedder()
    created_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as session:
        repo = EvidenceRepository(session=session)
        service = IngestionService(evidence_repo=repo, embedding_provider=embedder)

        for corpus_path in corpus_paths:
            raw_items = json.loads(corpus_path.read_text(encoding="utf-8"))
            for entry in raw_items:
                pub_date = (
                    date.fromisoformat(entry["publication_date"])
                    if entry.get("publication_date")
                    else None
                )
                doc_input = IngestionDocumentInput(
                    source_name=entry["source_name"],
                    source_url=entry["source_url"],
                    title=entry["title"],
                    authors=entry.get("authors"),
                    publication_date=pub_date,
                    language_code=entry.get("language_code", "id"),
                    source_type=entry["source_type"],
                    body_text=entry["body_text"],
                    is_synthetic_demo=bool(entry.get("is_synthetic_demo", False)),
                )
                _doc_id, created = await service.ingest_document(doc_input)
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        stats = await service.get_stats()
        print(
            f"Seed complete: created={created_count}, skipped_existing={skipped_count}, "
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
    args = parser.parse_args()
    paths = [args.corpus] if args.corpus is not None else CORPUS_PRESETS[args.preset]
    asyncio.run(seed_corpora(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
