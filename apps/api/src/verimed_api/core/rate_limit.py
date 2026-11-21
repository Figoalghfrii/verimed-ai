"""Sliding-window IP-based rate-limiting middleware returning ErrorResponse envelopes."""

import asyncio
import math
import time
from collections import defaultdict, deque

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from verimed_api.schemas.common import ErrorBody, ErrorResponse


class SlidingWindowRateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding-window rate limiter with standard rate-limit headers."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        enabled: bool = True,
        max_requests: int = 60,
        window_seconds: int = 60,
        exempt_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._enabled = enabled
        self._max_requests = max(1, max_requests)
        self._window_seconds = max(1, window_seconds)
        self._exempt_paths = exempt_paths or set()
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    @staticmethod
    def _extract_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            first_hop = forwarded_for.split(",", 1)[0].strip()
            if first_hop:
                return first_hop
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Throttle requests exceeding the per-IP sliding window limit."""
        if (
            not self._enabled
            or request.method == "OPTIONS"
            or request.url.path in self._exempt_paths
        ):
            return await call_next(request)

        client_ip = self._extract_client_ip(request)
        now = time.monotonic()
        window_start = now - self._window_seconds

        async with self._lock:
            bucket = self._hits[client_ip]
            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= self._max_requests:
                retry_after = max(1, math.ceil(bucket[0] + self._window_seconds - now))
                payload = ErrorResponse(
                    error=ErrorBody(
                        code="RATE_LIMIT_EXCEEDED",
                        message=(
                            "Terlalu banyak permintaan dalam waktu singkat. "
                            "Silakan coba lagi beberapa saat."
                        ),
                        details=[],
                    )
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=payload.model_dump(mode="json"),
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self._max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(retry_after),
                    },
                )

            bucket.append(now)
            remaining = max(0, self._max_requests - len(bucket))
            reset_seconds = max(1, math.ceil(bucket[0] + self._window_seconds - now))

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self._max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_seconds)
        return response
