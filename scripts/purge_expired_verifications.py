"""CLI script to purge expired verification records according to data retention policy."""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime, timedelta

from verimed_api.core.config import get_settings
from verimed_api.core.database import AsyncSessionLocal
from verimed_api.repositories.verification_repo import VerificationRepository


async def run_purge(retention_days: int) -> int:
    """Delete verification_requests older than `retention_days` and return removed count."""
    cutoff = datetime.now(tz=UTC) - timedelta(days=max(1, retention_days))
    async with AsyncSessionLocal() as session:
        repo = VerificationRepository(session=session)
        return await repo.purge_older_than(cutoff)


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(
        description="Purge expired VeriMed verification records from PostgreSQL."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=settings.data_retention_days,
        help="Retention period in days before verification_requests are purged.",
    )
    args = parser.parse_args()
    deleted = asyncio.run(run_purge(args.days))
    print(
        f"Purge complete: deleted_verification_requests={deleted}, retention_days={args.days}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
