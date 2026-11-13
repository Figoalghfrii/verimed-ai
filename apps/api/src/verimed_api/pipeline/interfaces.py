"""Protocol interfaces for VeriMed AI verification pipeline stages."""

from typing import Literal, Protocol

VerdictType = Literal[
    "SUPPORTED",
    "CONTRADICTED",
    "MIXED_EVIDENCE",
    "INSUFFICIENT_EVIDENCE",
]


class ClaimExtractorProtocol(Protocol):
    """Extracts atomic verifiable health claims from user text."""

    async def extract_claims(self, text: str) -> list[str]: ...
