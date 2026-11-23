"""Sliding-window IP-based rate-limiting middleware returning ErrorResponse envelopes."""

import asyncio
import ipaddress
import math
import time
from collections import OrderedDict, deque

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from verimed_api.core.logging import log_security_event
from verimed_api.schemas.common import ErrorBody, ErrorResponse


class SlidingWindowRateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding-window rate limiter with trusted-proxy extraction and bounded buckets."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        enabled: bool = True,
        max_requests: int = 60,
        window_seconds: int = 60,
        exempt_paths: set[str] | None = None,
        trusted_proxies: list[str] | tuple[str, ...] | None = None,
        route_limits: dict[str, int] | None = None,
        max_buckets: int = 10_000,
    ) -> None:
        super().__init__(app)
        self._enabled = enabled
        self._max_requests = max(1, max_requests)
        self._window_seconds = max(1, window_seconds)
        self._exempt_paths = exempt_paths or set()
        self._trusted_networks = self._parse_networks(trusted_proxies or [])
        self._route_limits = {
            prefix: max(1, limit) for prefix, limit in (route_limits or {}).items()
        }
        self._max_buckets = max(100, max_buckets)
        self._hits: OrderedDict[tuple[str, str], deque[float]] = OrderedDict()
        self._lock = asyncio.Lock()

    @staticmethod
    def _parse_networks(
        entries: list[str] | tuple[str, ...],
    ) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
        networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for raw in entries:
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                networks.append(ipaddress.ip_network(stripped, strict=False))
            except ValueError:
                continue
        return networks

    @staticmethod
    def _parse_ip(raw: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
        try:
            return ipaddress.ip_address(raw.strip())
        except ValueError:
            return None

    def _is_trusted_proxy(self, ip_text: str | None) -> bool:
        if not ip_text or not self._trusted_networks:
            return False
        ip_obj = self._parse_ip(ip_text)
        if ip_obj is None:
            return False
        return any(ip_obj in network for network in self._trusted_networks)

    def _extract_client_ip(self, request: Request) -> str:
        direct_ip = request.client.host if request.client and request.client.host else "unknown"
        if not self._is_trusted_proxy(direct_ip):
            return direct_ip

        forwarded_for = request.headers.get("x-forwarded-for")
        if not forwarded_for:
            return direct_ip

        hops = [hop.strip() for hop in forwarded_for.split(",") if hop.strip()]
        for hop in reversed(hops):
            hop_ip = self._parse_ip(hop)
            if hop_ip is None:
                return direct_ip
            if not any(hop_ip in network for network in self._trusted_networks):
                return str(hop_ip)
        return direct_ip

    def _resolve_bucket_limit(self, path: str) -> tuple[str, int]:
        best_prefix = ""
        best_limit = self._max_requests
        for prefix, limit in self._route_limits.items():
            if path.startswith(prefix) and len(prefix) > len(best_prefix):
                best_prefix = prefix
                best_limit = limit
        return (best_prefix or "default"), best_limit

    def _evict_if_full(self, window_start: float) -> None:
        if len(self._hits) < self._max_buckets:
            return
        stale_keys = [
            key for key, hits in self._hits.items() if not hits or hits[-1] <= window_start
        ]
        for key in stale_keys:
            self._hits.pop(key, None)
        while len(self._hits) >= self._max_buckets:
            self._hits.popitem(last=False)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Throttle requests exceeding the per-IP sliding window limit."""
        if (
            not self._enabled
            or request.method == "OPTIONS"
            or request.url.path in self._exempt_paths
        ):
            return await call_next(request)

        client_ip = self._extract_client_ip(request)
        tier, limit = self._resolve_bucket_limit(request.url.path)
        bucket_key = (tier, client_ip)
        now = time.monotonic()
        window_start = now - self._window_seconds

        async with self._lock:
            if bucket_key not in self._hits:
                self._evict_if_full(window_start)
                self._hits[bucket_key] = deque()
            else:
                self._hits.move_to_end(bucket_key)

            bucket = self._hits[bucket_key]
            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(1, math.ceil(bucket[0] + self._window_seconds - now))
                log_security_event(
                    "rate_limit_exceeded",
                    request_id=getattr(request.state, "request_id", None),
                    client_ip=client_ip,
                    outcome="throttled",
                    details={"tier": tier, "limit": limit, "path": request.url.path},
                )
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
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(retry_after),
                    },
                )

            bucket.append(now)
            remaining = max(0, limit - len(bucket))
            reset_seconds = max(1, math.ceil(bucket[0] + self._window_seconds - now))

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_seconds)
        return response
