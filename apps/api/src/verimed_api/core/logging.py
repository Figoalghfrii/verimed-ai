"""Privacy-preserving structured logging setup."""

import logging
import sys

from verimed_api.core.config import get_settings


def configure_logging() -> None:
    """Configure application-wide root logger without leaking sensitive user content."""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        stream=sys.stdout,
        force=True,
    )
