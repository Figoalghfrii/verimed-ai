"""Deterministic grounded assessor and explainer for hybrid PostgreSQL retrieval mode."""

import re
from dataclasses import replace

from verimed_api.pipeline.interfaces import (
    CitationEntry,
    CitationStanceType,
    EvidenceAssessmentResult,
    ExplanationDraft,
    RetrievedChunkCandidate,
    SafetyGuardProtocol,
    VerdictType,
)

CONTRADICTION_CUES_RE = re.compile(
    r"\b(tidak\s+efektif|tidak\s+terbukti|belum\s+ada\s+bukti|bukan\s+obat|"
    r"tidak\s+dapat\s+menyembuhkan|tidak\s+menggantikan|tidak\s+benar|tidak\s+aman|"
    r"mitos|keliru)\b",
    re.IGNORECASE,
)
SUPPORT_CUES_RE = re.compile(
    r"\b(membantu\s+menurunkan|terbukti\s+efektif|direkomendasikan|melindungi|"
    r"mencegah\s+penularan|aman\s+dan\s+efektif|dianjurkan)\b",
    re.IGNORECASE,
)
MIXED_CUES_RE = re.compile(
    r"\b(beragam|inkonsisten|bergantung\s+pada\s+kelompok|tidak\s+konsisten|"
    r"masih\s+terbatas|sebagian\s+studi)\b",
    re.IGNORECASE,
)


def _infer_chunk_stance(chunk_text: str) -> CitationStanceType:
    has_contra = bool(CONTRADICTION_CUES_RE.search(chunk_text))
    has_support = bool(SUPPORT_CUES_RE.search(chunk_text))
    if has_contra and not has_support:
        return "CONTRADICTING"
    if has_support and not has_contra:
        return "SUPPORTING"
    return "CONTEXTUAL"


class HybridGroundedAssessor:
    """Evaluates retrieved PostgreSQL chunks without external paid LLM calls."""

    def __init__(self, min_confidence_threshold: float = 0.35) -> None:
        self._min_confidence = min_confidence_threshold

    async def assess(
        self,
        claim_text: str,
        evidence: list[RetrievedChunkCandidate],
    ) -> EvidenceAssessmentResult:
        """Determine evidence verdict and enforce strict abstention when evidence is weak."""
        del claim_text
        if not evidence or evidence[0].rerank_score < self._min_confidence:
            return EvidenceAssessmentResult(
                verdict="INSUFFICIENT_EVIDENCE",
                confidence_score=0.0,
                abstained=True,
                abstention_reason=(
                    "Tidak ditemukan potongan bukti di basis data yang memenuhi ambang "
                    "relevansi minimum untuk menilai klaim ini."
                ),
                uncertainty_notes=(
                    "Sistem menahan diri (abstain) karena bukti terindeks di basis data "
                    "belum memadai."
                ),
            )

        top_score = evidence[0].rerank_score
        focused_evidence = [
            chunk
            for chunk in evidence
            if chunk.rerank_score >= max(self._min_confidence, top_score * 0.65)
        ] or [evidence[0]]

        stances = {_infer_chunk_stance(chunk.chunk_text) for chunk in focused_evidence}
        has_mixed_cue = any(MIXED_CUES_RE.search(chunk.chunk_text) for chunk in focused_evidence)

        if has_mixed_cue or ("SUPPORTING" in stances and "CONTRADICTING" in stances):
            verdict: VerdictType = "MIXED_EVIDENCE"
        elif "CONTRADICTING" in stances:
            verdict = "CONTRADICTED"
        elif "SUPPORTING" in stances:
            verdict = "SUPPORTED"
        else:
            return EvidenceAssessmentResult(
                verdict="INSUFFICIENT_EVIDENCE",
                confidence_score=round(top_score * 0.6, 2),
                abstained=True,
                abstention_reason=(
                    "Potongan bukti yang ditemukan hanya bersifat kontekstual tanpa posisi "
                    "yang cukup tegas."
                ),
                uncertainty_notes=(
                    "Diperlukan rujukan ilmiah tambahan untuk memastikan hubungan klaim ini "
                    "terhadap bukti."
                ),
            )

        return EvidenceAssessmentResult(
            verdict=verdict,
            confidence_score=round(min(0.95, top_score), 2),
            abstained=False,
            abstention_reason=None,
            uncertainty_notes=(
                "Penilaian ini dihasilkan dari pencarian hibrida basis data (tsvector + pgvector) "
                "berdasarkan dokumen yang terindeks saat ini."
            ),
        )


class HybridGroundedExplainer:
    """Produces grounded Bahasa Indonesia summaries isolating untrusted evidence passages."""

    def __init__(self, safety_guard: SafetyGuardProtocol) -> None:
        self._safety_guard = safety_guard

    async def explain(
        self,
        claim_text: str,
        assessment: EvidenceAssessmentResult,
        evidence: list[RetrievedChunkCandidate],
    ) -> ExplanationDraft:
        """Assemble grounded explanation referencing only retrieved evidence chunks."""
        del claim_text
        if assessment.abstained or not evidence:
            return ExplanationDraft(
                explanation=(
                    "Dari penelusuran basis data bukti saat ini, belum ditemukan rujukan yang "
                    "cukup kuat dan relevan untuk menyimpulkan klaim tersebut. Sistem menahan "
                    "diri (abstain) agar tidak menyajikan kesimpulan tanpa dasar bukti."
                ),
                citations=[],
            )

        citations: list[CitationEntry] = []
        for idx, chunk in enumerate(evidence[:3], start=1):
            key = f"[{idx}]"
            _isolated = self._safety_guard.wrap_untrusted_evidence(key, chunk.chunk_text)
            del _isolated
            inferred_stance = _infer_chunk_stance(chunk.chunk_text)
            citations.append(
                CitationEntry(
                    citation_key=key,
                    chunk=replace(chunk, stance=inferred_stance),
                )
            )

        if assessment.verdict == "SUPPORTED":
            lead = (
                "Berdasarkan potongan bukti yang ditemukan dari basis data terkurasi, "
                "klaim tersebut sejalan dengan informasi pada sumber utama [1]."
            )
        elif assessment.verdict == "CONTRADICTED":
            lead = (
                "Berdasarkan potongan bukti yang ditemukan dari basis data terkurasi, "
                "klaim tersebut bertentangan dengan informasi pada sumber rujukan [1]."
            )
        else:
            lead = (
                "Berdasarkan potongan bukti yang ditemukan dari basis data terkurasi, "
                "bukti ilmiah menunjukkan hasil yang beragam atau bergantung konteks [1]."
            )

        parts = [lead]
        if len(citations) >= 2:
            parts.append(
                "Sumber pendukung tambahan juga memberikan konteks dan batasan penerapan "
                "yang perlu diperhatikan [2]."
            )

        return ExplanationDraft(explanation=" ".join(parts), citations=citations)
