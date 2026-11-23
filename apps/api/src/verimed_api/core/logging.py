"""Privacy-preserving structured logging setup."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from verimed_api.core.config import get_settings

security_logger = logging.getLogger("verimed_api.security")


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


def log_security_event(
    event_type: str,
    *,
    request_id: str | None = None,
    client_ip: str | None = None,
    outcome: str = "blocked",
    details: dict[str, Any] | None = None,
) -> None:
    """Emit structured JSON security telemetry without logging PHI or secrets."""
    payload: dict[str, Any] = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "event_type": event_type,
        "outcome": outcome,
        "request_id": request_id,
        "client_ip": client_ip,
    }
    if details:
        payload["details"] = details
    security_logger.warning("%s", json.dumps(payload, default=str, ensure_ascii=True))
