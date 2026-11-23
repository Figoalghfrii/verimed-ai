"""Input sanitization, SSRF protection, privacy redaction, and HMAC token utilities."""

import base64
import hashlib
import hmac
import ipaddress
import json
import re
import socket
import time
from typing import Any
from urllib.parse import urlsplit

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "ip6-localhost",
    "ip6-loopback",
}


def sanitize_user_text(text: str) -> str:
    """Strip non-printable control characters and normalize whitespace."""
    cleaned = CONTROL_CHARS_RE.sub("", text)
    return cleaned.strip()


def redact_private_text(text: str) -> str:
    """Return non-reversible hash placeholder for private health claims at rest."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"[redacted-private-claim:{digest}]"


def _is_obfuscated_ip_host(hostname: str) -> bool:
    """Reject integer, hex, or octal-obfuscated IPv4 host representations."""
    if hostname.isdigit():
        return True
    parts = hostname.split(".")
    if 1 <= len(parts) <= 4 and all(part for part in parts):
        is_numeric_like = all(
            part.isdigit()
            or (
                part.startswith("0x")
                and len(part) > 2
                and all(c in "0123456789abcdef" for c in part[2:])
            )
            for part in parts
        )
        if is_numeric_like and any(
            part.startswith("0x") or (part.startswith("0") and len(part) > 1) for part in parts
        ):
            return True
    return False


def _is_disallowed_ip(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return True if an IP (including IPv4-mapped IPv6) is non-public or special-use."""
    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped is not None:
        ip_obj = ip_obj.ipv4_mapped
    return (
        not ip_obj.is_global
        or ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def is_safe_external_url(
    url: str,
    allowed_hosts: set[str] | None = None,
    *,
    resolve_dns: bool = False,
) -> bool:
    """Validate URL against SSRF risks (HTTPS only, no userinfo/non-443/private IPs)."""
    if not url or len(url) > 2048 or any(ch.isspace() for ch in url):
        return False

    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "https":
            return False
        if parsed.username is not None or parsed.password is not None:
            return False
        if parsed.port not in (None, 443):
            return False

        raw_hostname = parsed.hostname
        if not raw_hostname:
            return False
        hostname = raw_hostname.strip().lower().rstrip(".")
        if not hostname or hostname in BLOCKED_HOSTNAMES or _is_obfuscated_ip_host(hostname):
            return False

        if resolve_dns and (hostname.endswith(".local") or hostname.endswith(".internal")):
            return False

        try:
            ip = ipaddress.ip_address(hostname)
            if _is_disallowed_ip(ip):
                return False
        except ValueError:
            if resolve_dns:
                addrinfo = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
                if not addrinfo:
                    return False
                for _family, _kind, _proto, _canonname, sockaddr in addrinfo:
                    resolved_ip = ipaddress.ip_address(sockaddr[0])
                    if _is_disallowed_ip(resolved_ip):
                        return False

        if allowed_hosts is not None and hostname not in {h.lower() for h in allowed_hosts}:
            return False
        return True
    except (ValueError, OSError):
        return False


def validate_outbound_fetch_url(
    url: str,
    allowed_hosts: set[str] | None = None,
) -> bool:
    """Strictly validate a live outbound HTTP fetch target including DNS resolution."""
    return is_safe_external_url(url, allowed_hosts=allowed_hosts, resolve_dns=True)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(f"{encoded}{padding}".encode("ascii"))


def issue_signed_token(
    payload: dict[str, Any],
    *,
    secret: str,
    ttl_seconds: int,
) -> str:
    """Create a compact HMAC-SHA256 signed JSON token with expiration."""
    now = int(time.time())
    body = {
        **payload,
        "iat": now,
        "exp": now + max(1, ttl_seconds),
    }
    encoded_body = _b64url_encode(
        json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        encoded_body.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_body}.{_b64url_encode(signature)}"


def verify_signed_token(token: str, *, secret: str) -> dict[str, Any] | None:
    """Verify HMAC-SHA256 signature and expiration, returning payload dict or None."""
    if not token or "." not in token:
        return None
    try:
        encoded_body, encoded_sig = token.split(".", 1)
        expected_sig = hmac.new(
            secret.encode("utf-8"),
            encoded_body.encode("ascii"),
            hashlib.sha256,
        ).digest()
        provided_sig = _b64url_decode(encoded_sig)
        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload = json.loads(_b64url_decode(encoded_body).decode("utf-8"))
        if not isinstance(payload, dict):
            return None
        exp = payload.get("exp")
        if not isinstance(exp, int) or exp < int(time.time()):
            return None
        return payload
    except (ValueError, json.JSONDecodeError):
        return None
