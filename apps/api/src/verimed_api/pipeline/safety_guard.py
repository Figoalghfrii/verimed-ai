"""Emergency medical screening and prompt-injection defense utilities."""

import re

from verimed_api.core.security import sanitize_user_text
from verimed_api.pipeline.interfaces import SafetyCheckResult

EMERGENCY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "cardiac_respiratory",
        re.compile(
            r"\b(nyeri\s+dada(\s+hebat)?|serangan\s+jantung|sesak\s+napas(\s+berat|\s+akut)?|"
            r"sulit\s+bernapas|henti\s+jantung|chest\s+pain|shortness\s+of\s+breath)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "neurological_stroke",
        re.compile(
            r"\b(gejala\s+stroke|mulut\s+mencong|lumpuh\s+mendadak|kejang(\s+terus)?|"
            r"tidak\s+sadarkan\s+diri|pingsan\s+mendadak)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "trauma_poisoning",
        re.compile(
            r"\b(perdarahan\s+hebat|pendarahan\s+hebat|keracunan\s+akut|overdosis|"
            r"terbakar\s+hebat|anafilaksis)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "self_harm",
        re.compile(
            r"\b(bunuh\s+diri|menyakiti\s+diri(\s+sendiri)?|ingin\s+mati|mengakhiri\s+hidup)\b",
            re.IGNORECASE,
        ),
    ),
)

INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(ignore\s+(all\s+)?(previous|prior|system)\s+instructions?|"
        r"abaikan\s+(semua\s+)?instruksi\s+(sebelumnya|sistem)|"
        r"act\s+as\s+a\s+doctor|bertindaklah\s+sebagai\s+dokter|"
        r"<\s*/?\s*system\s*>|<\s*/?\s*untrusted_evidence[^>]*>)",
        re.IGNORECASE,
    ),
)


class SafetyGuard:
    """Screens untrusted user inputs and isolates untrusted evidence chunks."""

    def screen_input(self, text: str) -> SafetyCheckResult:
        """Sanitize input, strip prompt-injection phrases, and detect acute emergencies."""
        cleaned = sanitize_user_text(text)

        stripped_count = 0
        for pattern in INJECTION_PATTERNS:
            cleaned, count = pattern.subn(" ", cleaned)
            stripped_count += count

        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        for category, emergency_re in EMERGENCY_PATTERNS:
            if emergency_re.search(cleaned):
                return SafetyCheckResult(
                    is_emergency=True,
                    matched_category=category,
                    sanitized_text=cleaned,
                    injection_attempts_stripped=stripped_count,
                )

        return SafetyCheckResult(
            is_emergency=False,
            matched_category=None,
            sanitized_text=cleaned,
            injection_attempts_stripped=stripped_count,
        )

    def wrap_untrusted_evidence(self, citation_key: str, text: str) -> str:
        """Wrap retrieved passage in untrusted delimiters and neutralize nested tags."""
        safe_text = text.replace("<untrusted_evidence", "[untrusted_evidence").replace(
            "</untrusted_evidence>", "[/untrusted_evidence]"
        )
        for pattern in INJECTION_PATTERNS:
            safe_text = pattern.sub("[dihapus-demi-keamanan]", safe_text)
        return (
            f'<untrusted_evidence citation_key="{citation_key}">\n'
            f"{safe_text.strip()}\n"
            "</untrusted_evidence>"
        )
