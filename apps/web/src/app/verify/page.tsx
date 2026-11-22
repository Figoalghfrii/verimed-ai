"use client";

import React, { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { useVerifyClaim } from "@/features/verification/api/use-verify-claim";
import { AssessmentBadge } from "@/features/verification/components/assessment-badge";
import { ClaimInputForm } from "@/features/verification/components/claim-input-form";
import { VerificationResultView } from "@/features/verification/components/verification-result-view";
import {
  clearVerificationHistory,
  loadVerificationHistory,
  saveVerificationToHistory,
  VerificationHistoryEntry,
} from "@/features/verification/lib/verification-history";
import { VerificationResponseData } from "@/features/verification/schemas/verification-schema";

export default function VerifyPage() {
  const { mutate, data, isPending, isError, error } = useVerifyClaim();
  const [history, setHistory] = useState<VerificationHistoryEntry[]>([]);
  const [selectedHistoryResult, setSelectedHistoryResult] =
    useState<VerificationResponseData | null>(null);

  useEffect(() => {
    setHistory(loadVerificationHistory());
  }, []);

  useEffect(() => {
    if (data?.data && !data.data.emergency_triggered) {
      setSelectedHistoryResult(null);
      setHistory(saveVerificationToHistory(data.data));
    }
  }, [data]);

  const activeResult = selectedHistoryResult ?? data?.data ?? null;

  const handleClearHistory = () => {
    clearVerificationHistory();
    setHistory([]);
    setSelectedHistoryResult(null);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/80 bg-gradient-to-r from-white via-[#F7FAFF] to-[#EEF4FF] p-6 shadow-bento sm:p-7">
        <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
          <span className="h-2 w-2 rounded-full bg-brand-600" />
          Laboratorium Pemeriksaan Klaim
        </span>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Verifikasi Klaim Kesehatan
        </h1>
        <p className="mt-1.5 max-w-3xl text-sm leading-relaxed text-slate-600">
          Evaluasi klaim kesehatan terhadap bukti terkurasi dengan penilaian
          terkalibrasi, sitasi terverifikasi, dan penjelasan bahasa Indonesia
          yang transparan.
        </p>
      </section>

      <ClaimInputForm
        onSubmit={(payload) => {
          setSelectedHistoryResult(null);
          mutate(payload);
        }}
        isSubmitting={isPending}
      />

      {isPending && (
        <Card as="section" ariaLabelledBy="loading-status-heading">
          <div role="status" className="space-y-3">
            <h2
              id="loading-status-heading"
              className="text-sm font-bold text-slate-900"
            >
              Menjalankan Pipeline Verifikasi...
            </h2>
            <p className="text-sm text-slate-600">
              Memeriksa keselamatan darurat medis, mengekstrak klaim, mencari
              bukti relevan, dan memvalidasi sitasi.
            </p>
            <div className="h-3 w-3/4 animate-pulse rounded-full bg-slate-200" />
            <div className="h-3 w-1/2 animate-pulse rounded-full bg-slate-200" />
          </div>
        </Card>
      )}

      {isError && (
        <div
          role="alert"
          className="rounded-3xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-900 shadow-bento"
        >
          <p className="font-bold">
            Gagal memproses verifikasi klaim kesehatan
          </p>
          <p className="mt-1">
            {error instanceof Error
              ? error.message
              : "Pastikan layanan backend FastAPI berjalan pada port 8000."}
          </p>
        </div>
      )}

      {activeResult && !isPending && (
        <VerificationResultView result={activeResult} />
      )}

      {history.length > 0 && (
        <Card as="section" ariaLabelledBy="local-history-heading" className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2
                id="local-history-heading"
                className="text-sm font-bold text-slate-900"
              >
                Riwayat Pemeriksaan Lokal
              </h2>
              <p className="text-xs text-slate-600">
                Disimpan sementara hanya di browser Anda dan dapat dihapus kapan
                saja.
              </p>
            </div>
            <button
              type="button"
              onClick={handleClearHistory}
              className="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
            >
              Hapus Riwayat
            </button>
          </div>

          <ul className="space-y-2">
            {history.map((entry) => {
              const firstClaim = entry.result.claims[0];
              if (!firstClaim) return null;
              const isSelected =
                activeResult?.request_id === entry.result.request_id;
              return (
                <li key={entry.result.request_id}>
                  <button
                    type="button"
                    aria-current={isSelected ? "true" : undefined}
                    onClick={() => {
                      setSelectedHistoryResult(entry.result);
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                    className={`flex w-full flex-wrap items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                      isSelected
                        ? "border-brand-400 bg-brand-50/70"
                        : "border-slate-200/80 bg-canvas hover:border-brand-300 hover:bg-brand-50/40"
                    }`}
                  >
                    <span className="line-clamp-1 text-xs font-medium text-slate-800">
                      &ldquo;{firstClaim.claim_text}&rdquo;
                    </span>
                    <AssessmentBadge verdict={firstClaim.verdict} />
                  </button>
                </li>
              );
            })}
          </ul>
        </Card>
      )}
    </div>
  );
}
