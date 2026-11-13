"""Colloquial Indonesian-to-biomedical query normalization for Phase 2 MVP."""

import re

INDONESIAN_MEDICAL_SYNONYMS: dict[str, str] = {
    "sirsak": "daun sirsak annona muricata kanker kemoterapi",
    "kanker": "kanker neoplasma onkologi kemoterapi",
    "antibiotik": "antibiotik resistensi antimikroba infeksi bakteri virus",
    "flu": "influenza common cold infeksi saluran pernapasan virus",
    "pilek": "influenza common cold infeksi virus",
    "cuci tangan": "cuci tangan pakai sabun ctps higiene sanitasi infeksi diare",
    "sabun": "cuci tangan pakai sabun ctps pencegahan infeksi",
    "vitamin c": "vitamin c asam askorbat imunitas common cold flu",
    "vaksin": "vaksinasi imunisasi kekebalan tubuh pencegahan penyakit",
    "imunisasi": "vaksinasi imunisasi kekebalan kelompok pencegahan penyakit",
    "gula": "gula darah glukosa diabetes melitus",
    "kencing manis": "diabetes melitus glukosa darah",
    "darah tinggi": "hipertensi tekanan darah sistolik diastolik",
    "angin duduk": "angina pektoris sindrom koroner akut nyeri dada",
}

PUNCTUATION_RE = re.compile(r"[^\w\s-]", re.UNICODE)


class IndonesianQueryNormalizer:
    """Normalizes informal Bahasa Indonesia claims into enriched search queries."""

    async def normalize(self, claim_text: str) -> str:
        """Return lowercase normalized query augmented with medical synonyms."""
        cleaned = PUNCTUATION_RE.sub(" ", claim_text.lower())
        normalized = re.sub(r"\s+", " ", cleaned).strip()

        expansions: list[str] = []
        for term, synonym_group in INDONESIAN_MEDICAL_SYNONYMS.items():
            if term in normalized:
                expansions.append(synonym_group)

        if not expansions:
            return normalized
        return f"{normalized} | {' '.join(expansions)}"
