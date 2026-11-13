import React from "react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { VerificationResponseData } from "../schemas/verification-schema";
import { AssessmentBadge } from "./assessment-badge";
import { EmergencyAlert } from "./emergency-alert";
import { EvidenceSourceCard } from "./evidence-source-card";

export function VerificationResultView({
  result,
}: {
  result: VerificationResponseData;
}) {
  return (
    <section
      aria-labelledby="verification-result-heading"
      className="space-y-6"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2
          id="verification-result-heading"
          className="text-xl font-bold text-slate-900"
        >
          Hasil Pemeriksaan Bukti
        </h2>
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
          {result.is_demonstration && (
            <Badge variant="warning">Mode Demonstrasi (Data Simulasi)</Badge>
          )}
          <span className="rounded-full bg-white px-3 py-1 font-medium text-slate-600 shadow-sm">
            Waktu proses: {result.processing_time_ms} ms
          </span>
        </div>
      </div>

      {result.is_demonstration && (
        <div
          role="note"
          className="rounded-2xl border border-amber-200 bg-amber-50/90 p-4 text-sm text-amber-950"
        >
          <strong>Pemberitahuan Mode Demonstrasi:</strong> Sistem saat ini
          berjalan dengan penyedia data simulasi deterministik (
          <code className="rounded-md bg-amber-100 px-1.5 py-0.5 font-mono text-xs">
            {result.model_version}
          </code>
          ). Hasil ini hanya untuk mendemonstrasikan alur kerja pipeline VeriMed
          dan bukan merupakan penelusuran literatur klinis langsung.
        </div>
      )}

      {result.emergency_triggered && result.emergency_guidance && (
        <EmergencyAlert guidance={result.emergency_guidance} />
      )}

      {!result.emergency_triggered &&
        result.claims.map((claim) => (
          <Card key={claim.claim_index} as="article" className="space-y-5 sm:p-7">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 pb-5">
              <div className="space-y-1.5">
                <span className="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-brand-700">
                  Klaim #{claim.claim_index}
                </span>
                <p className="text-base font-bold text-slate-900">
                  &ldquo;{claim.claim_text}&rdquo;
                </p>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <AssessmentBadge verdict={claim.verdict} />
                <span className="text-xs font-medium text-slate-500">
                  Skor keyakinan bukti:{" "}
                  {Math.round(claim.confidence_score * 100)}%
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-bold text-slate-900">
                Penjelasan Berbasis Bukti
              </h3>
              <p className="text-sm leading-relaxed text-slate-700">
                {claim.explanation}
              </p>
            </div>

            {claim.abstained && claim.abstention_reason && (
              <div className="rounded-2xl border border-slate-200 bg-slate-100/80 p-4 text-sm text-slate-800">
                <strong>Alasan Sistem Menahan Diri (Abstain):</strong>{" "}
                {claim.abstention_reason}
              </div>
            )}

            <div className="rounded-2xl border border-brand-100 bg-brand-50/70 p-4 text-sm text-slate-800">
              <strong className="text-brand-900">
                Ketidakpastian &amp; Batasan:
              </strong>{" "}
              {claim.uncertainty_notes}
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">
                  Sumber Bukti Terkait ({claim.sources.length})
                </h3>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  Validasi sitasi:{" "}
                  {claim.citations_valid ? "Terverifikasi" : "Disaring"}
                </span>
              </div>

              {claim.sources.length === 0 ? (
                <p className="rounded-2xl border border-dashed border-slate-300 p-4 text-sm text-slate-600">
                  Tidak ada sumber bukti yang memenuhi ambang relevansi minimum
                  untuk klaim ini.
                </p>
              ) : (
                <div className="space-y-3">
                  {claim.sources.map((source) => (
                    <EvidenceSourceCard
                      key={source.chunk_id}
                      source={source}
                    />
                  ))}
                </div>
              )}
            </div>
          </Card>
        ))}

      <div
        role="note"
        className="rounded-2xl border border-brand-100 bg-white p-4 text-xs leading-relaxed text-slate-600 shadow-sm"
      >
        <strong className="text-slate-900">Penafian Medis:</strong>{" "}
        {result.disclaimer}
      </div>
    </section>
  );
}
