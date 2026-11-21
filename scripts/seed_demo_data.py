"""Reproducible CLI script to seed curated/synthetic evidence into PostgreSQL + pgvector."""

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


def _build_embedder() -> EmbeddingProviderProtocol:
    settings = get_settings()
    if settings.embedding_backend == "sentence_transformers":
        return SentenceTransformerEmbeddingProvider(
            model_name=settings.embedding_model_name
        )
    return DeterministicHashEmbeddingProvider(dimension=settings.embedding_dimension)


async def seed_corpus(corpus_path: Path) -> None:
    """Load JSON documents, chunk, embed, and upsert into PostgreSQL idempotently."""
    raw_items = json.loads(corpus_path.read_text(encoding="utf-8"))
    embedder = _build_embedder()

    created_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as session:
        repo = EvidenceRepository(session=session)
        service = IngestionService(evidence_repo=repo, embedding_provider=embedder)

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
            f"total_documents={stats.documents_count}, total_chunks={stats.chunks_count}"
        )


def main() -> int:
    default_path = (
        Path(__file__).resolve().parents[1]
        / "ml"
        / "data"
        / "synthetic_seed_evidence.json"
    )
    parser = argparse.ArgumentParser(
        description="Seed VeriMed evidence corpus into PostgreSQL."
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=default_path,
        help="Path to JSON corpus file.",
    )
    args = parser.parse_args()
    asyncio.run(seed_corpus(args.corpus))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
