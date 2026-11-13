"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { useVerifyClaim } from "@/features/verification/api/use-verify-claim";
import { ClaimInputForm } from "@/features/verification/components/claim-input-form";
import { VerificationResultView } from "@/features/verification/components/verification-result-view";

export default function VerifyPage() {
  const { mutate, data, isPending, isError, error } = useVerifyClaim();

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
        onSubmit={(payload) => mutate(payload)}
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

      {data && !isPending && <VerificationResultView result={data.data} />}
    </div>
  );
}
