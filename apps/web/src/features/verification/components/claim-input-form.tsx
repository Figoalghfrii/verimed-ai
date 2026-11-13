"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import {
  VerifyClaimInput,
  VerifyClaimInputSchema,
} from "../schemas/verification-schema";

const SAMPLE_DEMO_CLAIMS: readonly { label: string; text: string }[] = [
  {
    label: "Contoh Didukung Bukti",
    text: "Mencuci tangan pakai sabun dan air mengalir membantu menurunkan risiko penularan infeksi diare.",
  },
  {
    label: "Contoh Bertentangan",
    text: "Minum air rebusan daun sirsak dapat menyembuhkan semua jenis kanker tanpa kemoterapi.",
  },
  {
    label: "Contoh Bukti Beragam",
    text: "Konsumsi suplemen vitamin C dosis tinggi setiap hari mencegah pilek biasa.",
  },
  {
    label: "Contoh Bukti Tidak Cukup",
    text: "Mengonsumsi ekstrak tanaman eksotis langka dapat menambah tinggi badan orang dewasa.",
  },
];

interface ClaimInputFormProps {
  onSubmit: (payload: VerifyClaimInput) => void;
  isSubmitting: boolean;
}

export function ClaimInputForm({
  onSubmit,
  isSubmitting,
}: ClaimInputFormProps) {
  const [text, setText] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = VerifyClaimInputSchema.safeParse({ text, language: "id" });
    if (!parsed.success) {
      setValidationError(
        parsed.error.issues[0]?.message ?? "Klaim kesehatan tidak valid."
      );
      return;
    }
    setValidationError(null);
    onSubmit(parsed.data);
  };

  const handleSampleClick = (sampleText: string) => {
    setText(sampleText);
    setValidationError(null);
  };

  return (
    <Card as="section" ariaLabelledBy="claim-form-heading">
      <div className="space-y-4">
        <div>
          <h2
            id="claim-form-heading"
            className="text-lg font-semibold text-slate-900"
          >
            Masukkan Klaim Kesehatan untuk Diperiksa
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Tempelkan klaim dari media sosial atau pesan berantai (10–1.000
            karakter). Jangan masukkan data pribadi atau rekam medis.
          </p>
        </div>

        <div>
          <p className="text-xs font-medium text-slate-600">
            Coba contoh klaim demonstrasi:
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {SAMPLE_DEMO_CLAIMS.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => handleSampleClick(sample.text)}
                className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-brand-600 hover:bg-teal-50 hover:text-teal-900"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} noValidate className="space-y-3">
          <div>
            <label
              htmlFor="claim-text-input"
              className="block text-sm font-medium text-slate-800"
            >
              Teks Klaim Kesehatan
            </label>
            <textarea
              id="claim-text-input"
              name="text"
              rows={4}
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (validationError) setValidationError(null);
              }}
              placeholder="Contoh: Minum antibiotik dapat menyembuhkan flu biasa karena virus..."
              aria-invalid={validationError ? "true" : "false"}
              aria-describedby="claim-input-helper claim-input-error"
              className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
            />
            <div
              id="claim-input-helper"
              className="mt-1.5 flex items-center justify-between text-xs text-slate-500"
            >
              <span>Minimal 10 karakter, maksimal 1.000 karakter.</span>
              <span>{text.trim().length} / 1.000</span>
            </div>
            {validationError && (
              <p
                id="claim-input-error"
                role="alert"
                className="mt-1.5 text-xs font-medium text-rose-700"
              >
                {validationError}
              </p>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
            <button
              type="button"
              onClick={() => {
                setText("");
                setValidationError(null);
              }}
              disabled={isSubmitting || text.length === 0}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
            >
              Bersihkan
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:ring-offset-2 disabled:opacity-50"
            >
              {isSubmitting ? "Memeriksa Bukti..." : "Periksa Klaim"}
            </button>
          </div>
        </form>
      </div>
    </Card>
  );
}
