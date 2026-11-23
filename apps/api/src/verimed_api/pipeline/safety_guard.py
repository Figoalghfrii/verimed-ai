"""Emergency medical screening and prompt-injection defense utilities."""

import re

from verimed_api.core.security import sanitize_user_text
from verimed_api.pipeline.interfaces import SafetyCheckResult

EMERGENCY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "cardiac_respiratory",
        re.compile(
            r"\b(nyeri\s+dada(\s+hebat)?|sakit\s+dada(\s+hebat)?|"
            r"dada\s+(terasa\s+)?(berat|tertindih|tertekan)|serangan\s+jantung|"
            r"jantung\s+berdebar\s+kencang|nyeri\s+menjalar\s+ke\s+lengan|"
            r"sesak(\s+na[pf]as)?(\s+(berat|akut|sekali))?|sulit\s+berna[pf]as|"
            r"susah\s+(ber)?na[pf]as|tidak\s+bisa\s+(ber)?na[pf]as|henti\s+jantung|"
            r"(severe\s+|crushing\s+)?chest\s+pain|heart\s+attack|"
            r"shortness\s+of\s+breath|difficulty\s+breathing|trouble\s+breathing|"
            r"can'?t\s+breathe|cannot\s+breathe)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "neurological_stroke",
        re.compile(
            r"\b(gejala\s+stroke|mulut\s+mencong|wajah\s+mencong|"
            r"bicara\s+(mendadak\s+)?(pelo|cadel)|lumpuh\s+mendadak|kejang(\s+(terus|hebat))?|"
            r"tidak\s+sadarkan\s+diri|kehilangan\s+kesadaran|hilang\s+kesadaran|"
            r"pingsan(\s+mendadak)?|stroke\s+symptoms|slurred\s+speech|face\s+drooping|"
            r"sudden\s+paralysis|unconscious)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "trauma_poisoning",
        re.compile(
            r"\b(pendarahan\s+hebat|perdarahan\s+hebat|muntah\s+darah|batuk\s+darah|"
            r"keracunan\s+akut|overdosis(\s+obat)?|terbakar\s+hebat|anafilaksis|"
            r"tersengat\s+listrik|tenggelam|choking|vomiting\s+blood|coughing\s+up\s+blood|"
            r"severe\s+bleeding|acute\s+poisoning|overdose|anaphylaxis)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "self_harm",
        re.compile(
            r"\b((niat|mau|ingin)\s+bunuh\s+diri|bunuh\s+diri|menyakiti\s+diri(\s+sendiri)?|"
            r"ingin\s+(segera\s+)?mati|mau\s+mati\s+aja|(ingin\s+)?mengakhiri\s+hidup|"
            r"akhiri\s+hidup|suicide|self[\s-]harm|kill\s+myself|hurt\s+myself|"
            r"end\s+my\s+life|want\s+to\s+die)\b",
            re.IGNORECASE,
        ),
    ),
)

FUZZY_EMERGENCY_PHRASES: tuple[tuple[str, str], ...] = (
    ("cardiac_respiratory", "nyeri dada"),
    ("cardiac_respiratory", "sakit dada"),
    ("cardiac_respiratory", "sesak napas"),
    ("cardiac_respiratory", "serangan jantung"),
    ("cardiac_respiratory", "chest pain"),
    ("cardiac_respiratory", "heart attack"),
    ("neurological_stroke", "mulut mencong"),
    ("trauma_poisoning", "muntah darah"),
    ("trauma_poisoning", "batuk darah"),
    ("self_harm", "bunuh diri"),
    ("self_harm", "kill myself"),
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


def _levenshtein_max_one(a: str, b: str) -> bool:
    """Return True if edit distance between two normalized strings is <= 1."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    i = j = edits = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            edits += 1
            if edits > 1:
                return False
            if la > lb:
                i += 1
            elif lb > la:
                j += 1
            else:
                i += 1
                j += 1
    if i < la or j < lb:
        edits += 1
    return edits <= 1


def _normalize_emergency_text(text: str) -> str:
    lowered = text.lower().replace("nafas", "napas")
    collapsed = re.sub(r"(.)\1{2,}", r"\1", lowered)
    tokens = re.findall(r"[a-z0-9]+", collapsed)
    return " ".join(tokens)


def _match_emergency_category(cleaned: str) -> str | None:
    for category, emergency_re in EMERGENCY_PATTERNS:
        if emergency_re.search(cleaned):
            return category

    normalized = _normalize_emergency_text(cleaned)
    for category, emergency_re in EMERGENCY_PATTERNS:
        if emergency_re.search(normalized):
            return category

    tokens = normalized.split()
    for idx in range(len(tokens) - 1):
        bigram = f"{tokens[idx]} {tokens[idx + 1]}"
        for category, phrase in FUZZY_EMERGENCY_PHRASES:
            if _levenshtein_max_one(bigram, phrase):
                return category
    return None


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

        matched_category = _match_emergency_category(cleaned)
        if matched_category is not None:
            return SafetyCheckResult(
                is_emergency=True,
                matched_category=matched_category,
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
