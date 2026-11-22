"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import {
  VerifyClaimInput,
  VerifyClaimInputSchema,
} from "../schemas/verification-schema";

const SAMPLE_CLAIMS_BY_LANG: Record<
  "id" | "en",
  readonly { label: string; text: string }[]
> = {
  id: [
    {
      label: "Didukung Bukti",
      text: "Mencuci tangan pakai sabun dan air mengalir membantu menurunkan risiko penularan infeksi diare.",
    },
    {
      label: "Bertentangan",
      text: "Minum air rebusan daun sirsak dapat menyembuhkan semua jenis kanker tanpa kemoterapi.",
    },
    {
      label: "Bukti Beragam",
      text: "Konsumsi suplemen vitamin C dosis tinggi setiap hari mencegah pilek biasa.",
    },
    {
      label: "Bukti Tidak Cukup",
      text: "Mengonsumsi ekstrak tanaman eksotis langka dapat menambah tinggi badan orang dewasa.",
    },
    {
      label: "BPOM: Jamu Kanker",
      text: "Obat tradisional atau jamu tertentu dapat menyembuhkan penyakit kanker tanpa perlu operasi maupun terapi medis.",
    },
    {
      label: "Kemenkes: GGL",
      text: "Membatasi asupan gula, garam, dan lemak harian membantu menurunkan risiko diabetes dan hipertensi.",
    },
    {
      label: "Darurat Medis (119)",
      text: "Saya mengalami nyeri dada hebat yang menjalar dan sesak napas mendadak.",
    },
  ],
  en: [
    {
      label: "Handwashing & Infection",
      text: "Washing hands regularly with soap and running water reduces the risk of diarrhea and respiratory infections.",
    },
    {
      label: "Antibiotics for Cold",
      text: "Taking antibiotics can cure the common cold and flu caused by viruses.",
    },
    {
      label: "Soursop & Cancer",
      text: "Drinking boiled soursop leaf water cures all cancers without chemotherapy.",
    },
    {
      label: "Emergency (119)",
      text: "I am having severe chest pain and difficulty breathing right now.",
    },
  ],
};

interface ClaimInputFormProps {
  onSubmit: (payload: VerifyClaimInput) => void;
  isSubmitting: boolean;
}

export function ClaimInputForm({
  onSubmit,
  isSubmitting,
}: ClaimInputFormProps) {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState<"id" | "en">("id");
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = VerifyClaimInputSchema.safeParse({ text, language });
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
    <Card as="section" ariaLabelledBy="claim-form-heading" className="sm:p-7">
      <div className="space-y-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2
              id="claim-form-heading"
              className="text-lg font-bold text-slate-900"
            >
              Masukkan Klaim Kesehatan untuk Diperiksa
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Tempelkan klaim dari media sosial atau pesan berantai (10–1.000
              karakter). Jangan masukkan data pribadi atau rekam medis.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <label
              htmlFor="claim-language-select"
              className="text-xs font-semibold text-slate-600"
            >
              Bahasa Klaim:
            </label>
            <select
              id="claim-language-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value as "id" | "en")}
              className="rounded-full border border-slate-200 bg-canvas px-3 py-1.5 text-xs font-semibold text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
            >
              <option value="id">Bahasa Indonesia</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Contoh Klaim Demonstrasi &amp; Rujukan Publik
          </p>
          <div className="mt-2.5 flex flex-wrap gap-2">
            {SAMPLE_CLAIMS_BY_LANG[language].map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => handleSampleClick(sample.text)}
                className="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} noValidate className="space-y-3.5">
          <div>
            <label
              htmlFor="claim-text-input"
              className="block text-sm font-semibold text-slate-800"
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
              className="mt-2 w-full rounded-2xl border border-slate-200 bg-canvas/60 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 transition focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-500/10"
            />
            <div
              id="claim-input-helper"
              className="mt-2 flex items-center justify-between text-xs text-slate-500"
            >
              <span>Minimal 10 karakter, maksimal 1.000 karakter.</span>
              <span className="font-medium tabular-nums">
                {text.trim().length} / 1.000
              </span>
            </div>
            {validationError && (
              <p
                id="claim-input-error"
                role="alert"
                className="mt-1.5 text-xs font-semibold text-rose-700"
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
              className="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
            >
              Bersihkan
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center rounded-full bg-brand-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:ring-offset-2 disabled:opacity-50"
            >
              {isSubmitting ? "Memeriksa Bukti..." : "Periksa Klaim"}
            </button>
          </div>
        </form>
      </div>
    </Card>
  );
}
