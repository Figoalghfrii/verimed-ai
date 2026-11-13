"""Input sanitization and SSRF protection utilities."""

import ipaddress
import re
from urllib.parse import urlparse

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_user_text(text: str) -> str:
    """Strip non-printable control characters and normalize whitespace."""
    cleaned = CONTROL_CHARS_RE.sub("", text)
    return cleaned.strip()


def is_safe_external_url(url: str, allowed_hosts: set[str] | None = None) -> bool:
    """Validate URL against SSRF risks before any future external fetching."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"https"}:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname.lower() in {"localhost", "metadata.google.internal"}:
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
            ):
                return False
        except ValueError:
            pass
        if allowed_hosts is not None and hostname.lower() not in allowed_hosts:
            return False
        return True
    except Exception:
        return False
