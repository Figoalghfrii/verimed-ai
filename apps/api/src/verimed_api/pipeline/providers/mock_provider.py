"""Deterministic demonstration AI provider for Phase 2 local development and testing.

IMPORTANT: All evidence items returned by this module are synthetic demonstration records
explicitly flagged with `is_synthetic_demo=True` so they are never mistaken for live
clinical literature.
"""

from dataclasses import dataclass
from datetime import date

from verimed_api.pipeline.interfaces import (
    CitationEntry,
    EvidenceAssessmentResult,
    ExplanationDraft,
    RetrievedChunkCandidate,
    SafetyGuardProtocol,
    VerdictType,
)


@dataclass(frozen=True)
class _DemoTopicEntry:
    keywords: tuple[str, ...]
    expected_verdict: VerdictType
    chunks: tuple[RetrievedChunkCandidate, ...]
    uncertainty_notes: str


_DEMO_TOPICS: tuple[_DemoTopicEntry, ...] = (
    _DemoTopicEntry(
        keywords=("cuci tangan", "sabun", "ctps", "higiene"),
        expected_verdict="SUPPORTED",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-ctps-001",
                source_name="VeriMed Demo Corpus — Ringkasan Kebersihan Tangan",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                title=(
                    "[Contoh Simulasi] Efektivitas Cuci Tangan Pakai Sabun dalam Pencegahan Infeksi"
                ),
                source_url="https://demo.verimed.local/synthetic/ctps-infeksi",
                publication_date=date(2025, 1, 15),
                chunk_text=(
                    "Data simulasi demonstrasi: Kebiasaan mencuci tangan menggunakan sabun dan "
                    "air mengalir secara teratur membantu menurunkan risiko penularan infeksi "
                    "saluran pencernaan seperti diare serta infeksi saluran pernapasan."
                ),
                lexical_score=0.89,
                vector_score=0.91,
                hybrid_score=0.90,
                rerank_score=0.92,
                stance="SUPPORTING",
                is_synthetic_demo=True,
            ),
            RetrievedChunkCandidate(
                chunk_id="demo-ctps-002",
                source_name="VeriMed Demo Corpus — Sanitasi Komunitas",
                source_type="SYNTHETIC_DEMO_REVIEW",
                title="[Contoh Simulasi] Praktik Higiene Tangan di Lingkungan Rumah Tangga",
                source_url="https://demo.verimed.local/synthetic/higiene-rumah-tangga",
                publication_date=date(2024, 11, 20),
                chunk_text=(
                    "Data simulasi demonstrasi: Sabun membantu melarutkan lapisan lemak pada "
                    "permukaan patogen dan mempermudah pembilasan mikroorganisme dari kulit."
                ),
                lexical_score=0.78,
                vector_score=0.82,
                hybrid_score=0.80,
                rerank_score=0.84,
                stance="SUPPORTING",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Efektivitas pencegahan "
            "infeksi di dunia nyata tetap bergantung pada durasi mencuci tangan (minimal 20 detik) "
            "serta akses terhadap air bersih."
        ),
    ),
    _DemoTopicEntry(
        keywords=("sirsak", "annona muricata"),
        expected_verdict="CONTRADICTED",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-sirsak-001",
                source_name="VeriMed Demo Corpus — Edukasi Onkologi",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                title="[Contoh Simulasi] Evaluasi Klaim Ekstrak Daun Sirsak terhadap Kanker",
                source_url="https://demo.verimed.local/synthetic/daun-sirsak-kanker",
                publication_date=date(2025, 2, 10),
                chunk_text=(
                    "Data simulasi demonstrasi: Belum ada bukti uji klinis pada manusia yang "
                    "membuktikan bahwa rebusan daun sirsak dapat menyembuhkan semua jenis kanker "
                    "atau menggantikan terapi medis standar seperti kemoterapi dan radioterapi."
                ),
                lexical_score=0.92,
                vector_score=0.90,
                hybrid_score=0.91,
                rerank_score=0.94,
                stance="CONTRADICTING",
                is_synthetic_demo=True,
            ),
            RetrievedChunkCandidate(
                chunk_id="demo-sirsak-002",
                source_name="VeriMed Demo Corpus — Keamanan Terapi Herbal",
                source_type="SYNTHETIC_DEMO_REVIEW",
                title="[Contoh Simulasi] Batasan Penelitian Praklinis vs Uji Klinis Manusia",
                source_url="https://demo.verimed.local/synthetic/praklinis-vs-klinis",
                publication_date=date(2024, 9, 5),
                chunk_text=(
                    "Data simulasi demonstrasi: Efek sitotoksik yang diamati pada cawan petri "
                    "di laboratorium tidak otomatis berarti aman atau efektif sebagai pengobatan "
                    "kanker pada tubuh manusia, dan menunda terapi medis dapat memperburuk "
                    "prognosis."
                ),
                lexical_score=0.81,
                vector_score=0.85,
                hybrid_score=0.83,
                rerank_score=0.87,
                stance="CONTRADICTING",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Keputusan terapi kanker harus "
            "selalu dikonsultasikan dengan dokter spesialis onkologi."
        ),
    ),
    _DemoTopicEntry(
        keywords=("antibiotik",),
        expected_verdict="CONTRADICTED",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-abx-001",
                source_name="VeriMed Demo Corpus — Pengendalian Resistensi Antimikroba",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                title="[Contoh Simulasi] Penggunaan Antibiotik pada Infeksi Virus vs Bakteri",
                source_url="https://demo.verimed.local/synthetic/antibiotik-virus",
                publication_date=date(2025, 3, 1),
                chunk_text=(
                    "Data simulasi demonstrasi: Antibiotik dirancang untuk mengatasi infeksi "
                    "bakteri dan tidak efektif menyembuhkan flu atau pilek biasa yang disebabkan "
                    "oleh virus."
                ),
                lexical_score=0.91,
                vector_score=0.88,
                hybrid_score=0.895,
                rerank_score=0.93,
                stance="CONTRADICTING",
                is_synthetic_demo=True,
            ),
            RetrievedChunkCandidate(
                chunk_id="demo-abx-002",
                source_name="VeriMed Demo Corpus — Edukasi Penggunaan Obat Rasional",
                source_type="SYNTHETIC_DEMO_REVIEW",
                title="[Contoh Simulasi] Risiko Resistensi Antimikroba Akibat Konsumsi Tidak Tepat",
                source_url="https://demo.verimed.local/synthetic/resistensi-antimikroba",
                publication_date=date(2024, 12, 12),
                chunk_text=(
                    "Data simulasi demonstrasi: Penggunaan antibiotik tanpa indikasi medis dan "
                    "resep dokter meningkatkan risiko resistensi bakteri sehingga infeksi di masa "
                    "depan menjadi lebih sulit diobati."
                ),
                lexical_score=0.80,
                vector_score=0.83,
                hybrid_score=0.815,
                rerank_score=0.85,
                stance="CONTEXTUAL",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Hanya tenaga medis yang dapat "
            "menentukan apakah gejala infeksi membutuhkan antibiotik."
        ),
    ),
    _DemoTopicEntry(
        keywords=("vitamin c", "asam askorbat"),
        expected_verdict="MIXED_EVIDENCE",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-vitc-001",
                source_name="VeriMed Demo Corpus — Tinjauan Suplemen Harian",
                source_type="SYNTHETIC_DEMO_REVIEW",
                title="[Contoh Simulasi] Suplementasi Vitamin C untuk Pencegahan Pilek",
                source_url="https://demo.verimed.local/synthetic/vitamin-c-pencegahan",
                publication_date=date(2025, 1, 28),
                chunk_text=(
                    "Data simulasi demonstrasi: Pada populasi umum, konsumsi rutin suplemen "
                    "vitamin C dosis tinggi tidak terbukti secara konsisten mencegah timbulnya "
                    "pilek biasa."
                ),
                lexical_score=0.87,
                vector_score=0.85,
                hybrid_score=0.86,
                rerank_score=0.88,
                stance="CONTRADICTING",
                is_synthetic_demo=True,
            ),
            RetrievedChunkCandidate(
                chunk_id="demo-vitc-002",
                source_name="VeriMed Demo Corpus — Nutrisi & Durasi Gejala",
                source_type="SYNTHETIC_DEMO_REVIEW",
                title=(
                    "[Contoh Simulasi] Dampak Vitamin C terhadap Lama Gejala pada Kelompok Tertentu"
                ),
                source_url="https://demo.verimed.local/synthetic/vitamin-c-durasi",
                publication_date=date(2024, 10, 4),
                chunk_text=(
                    "Data simulasi demonstrasi: Beberapa ringkasan bukti menunjukkan suplementasi "
                    "rutin berpotensi sedikit mempersingkat durasi gejala pada kelompok tertentu, "
                    "sehingga temuan mengenai manfaat keseluruhannya bersifat beragam."
                ),
                lexical_score=0.83,
                vector_score=0.84,
                hybrid_score=0.835,
                rerank_score=0.86,
                stance="SUPPORTING",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Dosis tinggi vitamin C dalam "
            "jangka panjang dapat menimbulkan efek samping pencernaan atau risiko pada individu "
            "dengan kondisi ginjal tertentu."
        ),
    ),
    _DemoTopicEntry(
        keywords=("imunisasi", "vaksin", "campak", "measles", "vaccine"),
        expected_verdict="SUPPORTED",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-imun-001",
                source_name="VeriMed Demo Corpus — Imunisasi Dasar",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                title="[Contoh Simulasi] Peran Imunisasi Dasar dalam Pencegahan Penyakit Menular",
                source_url="https://demo.verimed.local/synthetic/imunisasi-dasar",
                publication_date=date(2025, 2, 20),
                chunk_text=(
                    "Data simulasi demonstrasi: Imunisasi dasar direkomendasikan dan terbukti "
                    "efektif melindungi anak serta masyarakat dari berbagai penyakit menular "
                    "berbahaya seperti campak, polio, dan difteri."
                ),
                lexical_score=0.91,
                vector_score=0.90,
                hybrid_score=0.905,
                rerank_score=0.93,
                stance="SUPPORTING",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Jadwal imunisasi anak "
            "sebaiknya dikonsultasikan dengan puskesmas atau dokter anak."
        ),
    ),
    _DemoTopicEntry(
        keywords=("jamu", "obat tradisional", "herbal", "bko"),
        expected_verdict="CONTRADICTED",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-jamu-001",
                source_name="VeriMed Demo Corpus — Pengawasan Obat Bahan Alam",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                title=(
                    "[Contoh Simulasi] Evaluasi Klaim Obat Tradisional/Jamu "
                    "sebagai Penyembuh Kanker"
                ),
                source_url="https://demo.verimed.local/synthetic/jamu-kanker-bpom",
                publication_date=date(2025, 3, 5),
                chunk_text=(
                    "Data simulasi demonstrasi: Klaim promosi obat tradisional atau jamu dapat "
                    "menyembuhkan kanker tanpa terapi medis standar adalah tidak benar dan "
                    "tidak menggantikan penanganan medis dokter."
                ),
                lexical_score=0.90,
                vector_score=0.89,
                hybrid_score=0.895,
                rerank_score=0.92,
                stance="CONTRADICTING",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Pastikan produk memiliki "
            "izin edar resmi dan konsultasikan pengobatan penyakit berat dengan dokter."
        ),
    ),
    _DemoTopicEntry(
        keywords=("ggl", "gula", "garam", "lemak", "diabetes", "hipertensi"),
        expected_verdict="SUPPORTED",
        chunks=(
            RetrievedChunkCandidate(
                chunk_id="demo-ggl-001",
                source_name="VeriMed Demo Corpus — Gizi Seimbang PTM",
                source_type="SYNTHETIC_DEMO_GUIDELINE",
                title="[Contoh Simulasi] Pembatasan Gula, Garam, dan Lemak untuk Mencegah PTM",
                source_url="https://demo.verimed.local/synthetic/pembatasan-ggl",
                publication_date=date(2025, 2, 12),
                chunk_text=(
                    "Data simulasi demonstrasi: Membatasi asupan gula, garam, dan lemak harian "
                    "terbukti membantu menurunkan risiko penyakit tidak menular seperti diabetes "
                    "melitus tipe 2 dan hipertensi."
                ),
                lexical_score=0.89,
                vector_score=0.88,
                hybrid_score=0.885,
                rerank_score=0.91,
                stance="SUPPORTING",
                is_synthetic_demo=True,
            ),
        ),
        uncertainty_notes=(
            "Penilaian ini menggunakan data simulasi demonstrasi. Kebutuhan gizi harian "
            "dapat berbeda bagi individu dengan kondisi metabolik khusus."
        ),
    ),
)


class MockPipelineProvider:
    """Deterministic Phase 2 mock provider for retrieval, reranking, assessment, and explanation."""

    def __init__(self, safety_guard: SafetyGuardProtocol) -> None:
        self._safety_guard = safety_guard

    def _find_topic(self, normalized_query: str) -> _DemoTopicEntry | None:
        lowered = normalized_query.lower()
        for topic in _DEMO_TOPICS:
            if any(keyword in lowered for keyword in topic.keywords):
                return topic
        return None

    async def retrieve(
        self,
        claim_text: str,
        normalized_query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunkCandidate]:
        """Return deterministic synthetic chunks matching the normalized query."""
        del claim_text
        topic = self._find_topic(normalized_query)
        if topic is None:
            return []
        return list(topic.chunks[:top_k])

    async def rerank(
        self,
        claim_text: str,
        candidates: list[RetrievedChunkCandidate],
        min_score: float = 0.35,
    ) -> list[RetrievedChunkCandidate]:
        """Sort candidates by rerank_score descending and drop chunks below min_score."""
        del claim_text
        filtered = [c for c in candidates if c.rerank_score >= min_score]
        return sorted(filtered, key=lambda c: c.rerank_score, reverse=True)

    async def assess(
        self,
        claim_text: str,
        evidence: list[RetrievedChunkCandidate],
        language: str = "id",
    ) -> EvidenceAssessmentResult:
        """Assess stance from reranked evidence, enforcing abstention when evidence is missing."""
        del claim_text
        if not evidence:
            if language == "en":
                return EvidenceAssessmentResult(
                    verdict="INSUFFICIENT_EVIDENCE",
                    confidence_score=0.0,
                    abstained=True,
                    abstention_reason=(
                        "No evidence passages met the minimum relevance threshold in the "
                        "current demonstration corpus."
                    ),
                    uncertainty_notes=(
                        "The system abstained because available demonstration evidence is "
                        "insufficient to evaluate this claim."
                    ),
                )
            return EvidenceAssessmentResult(
                verdict="INSUFFICIENT_EVIDENCE",
                confidence_score=0.0,
                abstained=True,
                abstention_reason=(
                    "Tidak ditemukan potongan bukti yang memenuhi ambang relevansi minimum "
                    "dalam korpus demonstrasi saat ini."
                ),
                uncertainty_notes=(
                    "Sistem menahan diri dari kesimpulan (abstain) karena bukti dalam korpus "
                    "demonstrasi belum mencukupi untuk mengevaluasi klaim ini."
                ),
            )

        stances = {chunk.stance for chunk in evidence}
        top_score = evidence[0].rerank_score

        if "SUPPORTING" in stances and "CONTRADICTING" in stances:
            verdict: VerdictType = "MIXED_EVIDENCE"
        elif "CONTRADICTING" in stances:
            verdict = "CONTRADICTED"
        elif "SUPPORTING" in stances:
            verdict = "SUPPORTED"
        else:
            return EvidenceAssessmentResult(
                verdict="INSUFFICIENT_EVIDENCE",
                confidence_score=round(top_score * 0.5, 2),
                abstained=True,
                abstention_reason=(
                    "Retrieved passages are contextual only without a clear supporting or "
                    "refuting stance."
                    if language == "en"
                    else "Bukti yang ditemukan hanya bersifat kontekstual tanpa sikap jelas."
                ),
                uncertainty_notes=(
                    "Available evidence is not specific enough to support or contradict this claim."
                    if language == "en"
                    else (
                        "Bukti yang tersedia belum cukup spesifik untuk mendukung atau "
                        "membantah klaim."
                    )
                ),
            )

        # Look up topic-specific uncertainty notes when available
        topic_notes = (
            "This assessment was generated in demonstration mode using synthetic data and "
            "reflects only the sample corpus."
            if language == "en"
            else (
                "Penilaian ini dihasilkan oleh mode demonstrasi menggunakan data simulasi "
                "dan hanya mencerminkan isi korpus contoh."
            )
        )
        if language != "en":
            for topic in _DEMO_TOPICS:
                if evidence[0].chunk_id in {c.chunk_id for c in topic.chunks}:
                    topic_notes = topic.uncertainty_notes
                    break

        return EvidenceAssessmentResult(
            verdict=verdict,
            confidence_score=round(min(top_score, 0.95), 2),
            abstained=False,
            abstention_reason=None,
            uncertainty_notes=topic_notes,
        )

    async def explain(
        self,
        claim_text: str,
        assessment: EvidenceAssessmentResult,
        evidence: list[RetrievedChunkCandidate],
        language: str = "id",
    ) -> ExplanationDraft:
        """Generate grounded Indonesian or English explanation isolated from untrusted chunks."""
        del claim_text
        if assessment.abstained or not evidence:
            if language == "en":
                return ExplanationDraft(
                    explanation=(
                        "In current demonstration mode, VeriMed did not find sufficient evidence "
                        "in the sample database to evaluate this claim accurately. Therefore, the "
                        "system abstained to avoid unsupported conclusions."
                    ),
                    citations=[],
                )
            return ExplanationDraft(
                explanation=(
                    "Pada mode demonstrasi saat ini, VeriMed belum menemukan bukti yang cukup "
                    "dalam basis data contoh untuk menilai klaim tersebut secara akurat. Oleh "
                    "karena itu, sistem menahan diri (abstain) agar tidak memberikan kesimpulan "
                    "yang tidak berdasar."
                ),
                citations=[],
            )

        # Isolate retrieved text inside untrusted delimiters before assembling summary
        citations: list[CitationEntry] = []
        for idx, chunk in enumerate(evidence, start=1):
            key = f"[{idx}]"
            _isolated_block = self._safety_guard.wrap_untrusted_evidence(key, chunk.chunk_text)
            del _isolated_block
            citations.append(CitationEntry(citation_key=key, chunk=chunk))

        if language == "en":
            if assessment.verdict == "SUPPORTED":
                lead = (
                    "Based on retrieved synthetic demonstration evidence, the claim aligns with "
                    "the available summary [1]."
                )
            elif assessment.verdict == "CONTRADICTED":
                lead = (
                    "Based on retrieved synthetic demonstration evidence, the claim contradicts "
                    "findings in the demonstration corpus [1]."
                )
            else:
                lead = (
                    "Based on retrieved synthetic demonstration evidence, available findings are "
                    "mixed depending on context and population group [1]."
                )
            detail_parts = [lead]
            if len(citations) >= 2:
                detail_parts.append(
                    "Additional context from the second source clarifies application limits "
                    "and relevant medical safety considerations [2]."
                )
            return ExplanationDraft(explanation=" ".join(detail_parts), citations=citations)

        if assessment.verdict == "SUPPORTED":
            lead = (
                "Berdasarkan bukti simulasi demonstrasi yang ditemukan, klaim tersebut sejalan "
                "dengan ringkasan bukti yang tersedia [1]."
            )
        elif assessment.verdict == "CONTRADICTED":
            lead = (
                "Berdasarkan bukti simulasi demonstrasi yang ditemukan, klaim tersebut "
                "bertentangan dengan temuan medis pada korpus contoh [1]."
            )
        else:
            lead = (
                "Berdasarkan bukti simulasi demonstrasi yang ditemukan, bukti yang tersedia "
                "menunjukkan temuan yang beragam bergantung pada konteks dan kelompok populasi [1]."
            )

        detail_parts = [lead]
        if len(citations) >= 2:
            detail_parts.append(
                "Konteks tambahan dari sumber kedua menjelaskan batasan penerapan serta "
                "pertimbangan keselamatan medis yang relevan [2]."
            )

        return ExplanationDraft(
            explanation=" ".join(detail_parts),
            citations=citations,
        )
