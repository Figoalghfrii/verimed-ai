"""Colloquial Indonesian-to-biomedical query normalization for hybrid retrieval."""

import re

INDONESIAN_MEDICAL_SYNONYMS: dict[str, str] = {
    "sirsak": "daun sirsak annona muricata kanker kemoterapi",
    "kanker": "kanker neoplasma onkologi kemoterapi",
    "jamu": "obat tradisional jamu herbal bpom uji klinis",
    "herbal": "obat bahan alam tradisional jamu bpom keamanan",
    "obat tradisional": "obat tradisional jamu herbal bpom uji klinis",
    "bko": "bahan kimia obat obat bahan alam ilegal bpom",
    "bahan kimia obat": "bko obat bahan alam ilegal bpom deksametason sildenafil",
    "antibiotik": "antibiotik resistensi antimikroba amr infeksi bakteri virus",
    "flu": "influenza common cold infeksi saluran pernapasan virus",
    "pilek": "influenza common cold infeksi virus",
    "cuci tangan": "cuci tangan pakai sabun ctps higiene sanitasi infeksi diare",
    "sabun": "cuci tangan pakai sabun ctps pencegahan infeksi",
    "diare": "diare infeksi saluran pencernaan ctps cuci tangan sanitasi",
    "vitamin c": "vitamin c asam askorbat imunitas common cold flu",
    "vaksin": "vaksinasi imunisasi kekebalan tubuh pencegahan penyakit",
    "imunisasi": "vaksinasi imunisasi kekebalan kelompok pencegahan penyakit",
    "campak": "campak measles rubella vaksinasi imunisasi virus menular",
    "mmr": "vaksin mmr campak autisme keamanan vaksinasi",
    "autisme": "autisme vaksin mmr keamanan imunisasi",
    "gula": "gula darah glukosa ggl diabetes melitus resistensi insulin",
    "kencing manis": "diabetes melitus glukosa darah gula",
    "diabetes": "diabetes melitus gula darah resistensi insulin ggl",
    "garam": "garam natrium sodium hipertensi tekanan darah ggl",
    "natrium": "garam natrium hipertensi tekanan darah",
    "lemak": "lemak jenuh kolesterol penyakit jantung ggl",
    "darah tinggi": "hipertensi tekanan darah sistolik diastolik garam natrium",
    "hipertensi": "hipertensi tekanan darah garam natrium stroke jantung",
    "angin duduk": "angina pektoris sindrom koroner akut nyeri dada",
    "handwashing": "cuci tangan pakai sabun ctps higiene sanitasi infeksi diare",
    "wash hands": "cuci tangan pakai sabun ctps pencegahan infeksi diare",
    "soap": "sabun cuci tangan pakai sabun ctps pencegahan infeksi",
    "antibiotic": "antibiotik resistensi antimikroba amr infeksi bakteri virus",
    "soursop": "daun sirsak annona muricata kanker kemoterapi",
    "cancer": "kanker neoplasma onkologi kemoterapi",
    "vaccine": "vaksinasi imunisasi kekebalan tubuh pencegahan penyakit",
    "vaccination": "vaksinasi imunisasi kekebalan kelompok pencegahan penyakit",
    "immunization": "imunisasi vaksinasi kekebalan kelompok pencegahan penyakit",
    "measles": "campak measles rubella vaksinasi imunisasi",
    "sugar": "gula gula darah glukosa ggl diabetes melitus",
    "salt": "garam natrium sodium hipertensi tekanan darah ggl",
    "hypertension": "hipertensi darah tinggi tekanan darah garam natrium",
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
