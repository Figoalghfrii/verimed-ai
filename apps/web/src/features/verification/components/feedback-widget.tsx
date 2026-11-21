"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { useSubmitFeedback } from "../api/use-submit-feedback";
import { FeedbackCategory, FeedbackInputSchema } from "../schemas/feedback-schema";

const CATEGORY_OPTIONS: Array<{ value: FeedbackCategory; label: string }> = [
  { value: "CLARITY", label: "Kejelasan penjelasan" },
  { value: "CITATIONS", label: "Kelengkapan & kualitas sitasi" },
  { value: "ACCURACY_CONCERN", label: "Kekhawatiran akurasi informasi" },
  { value: "OTHER", label: "Lainnya" },
];

export function FeedbackWidget({
  requestId,
  persisted,
}: {
  requestId: string;
  persisted: boolean;
}) {
  const [selectedHelpful, setSelectedHelpful] = useState<boolean | null>(null);
  const [category, setCategory] = useState<FeedbackCategory>("CLARITY");
  const [comment, setComment] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [localSubmittedMessage, setLocalSubmittedMessage] = useState<
    string | null
  >(null);

  const { mutate, data, isPending, isError, error } = useSubmitFeedback();

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (selectedHelpful === null) {
      setValidationError("Pilih terlebih dahulu apakah penjelasan ini membantu.");
      return;
    }

    const parsed = FeedbackInputSchema.safeParse({
      request_id: requestId,
      is_helpful: selectedHelpful,
      feedback_category: category,
      comment: comment.trim() ? comment.trim() : null,
    });

    if (!parsed.success) {
      setValidationError(
        parsed.error.issues[0]?.message ?? "Masukan tidak valid."
      );
      return;
    }

    setValidationError(null);

    if (!persisted) {
      setLocalSubmittedMessage(
        "Terima kasih! Masukan Anda dicatat untuk sesi demonstrasi saat ini (mode stateless tanpa basis data)."
      );
      return;
    }

    mutate(parsed.data);
  };

  const submittedMessage = data?.data.message ?? localSubmittedMessage;

  return (
    <Card as="section" ariaLabelledBy="feedback-widget-heading" className="space-y-4">
      <div className="space-y-1">
        <h3
          id="feedback-widget-heading"
          className="text-sm font-bold text-slate-900"
        >
          Apakah penjelasan verifikasi ini mudah dipahami?
        </h3>
        <p className="text-xs text-slate-600">
          Penilaian Anda bersifat anonim dan membantu peningkatan kejelasan
          informasi VeriMed. Jangan sertakan data pribadi atau informasi medis
          sensitif.
        </p>
      </div>

      {submittedMessage ? (
        <div
          role="status"
          className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900"
        >
          {submittedMessage}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              aria-pressed={selectedHelpful === true}
              onClick={() => {
                setSelectedHelpful(true);
                setValidationError(null);
              }}
              className={`rounded-full border px-4 py-2 text-xs font-semibold transition ${
                selectedHelpful === true
                  ? "border-emerald-600 bg-emerald-600 text-white"
                  : "border-slate-200 bg-white text-slate-700 hover:border-emerald-300 hover:bg-emerald-50"
              }`}
            >
              Ya, Membantu
            </button>
            <button
              type="button"
              aria-pressed={selectedHelpful === false}
              onClick={() => {
                setSelectedHelpful(false);
                setValidationError(null);
              }}
              className={`rounded-full border px-4 py-2 text-xs font-semibold transition ${
                selectedHelpful === false
                  ? "border-rose-600 bg-rose-600 text-white"
                  : "border-slate-200 bg-white text-slate-700 hover:border-rose-300 hover:bg-rose-50"
              }`}
            >
              Kurang Membantu
            </button>
          </div>

          {selectedHelpful !== null && (
            <div className="space-y-3 rounded-2xl border border-slate-200/80 bg-canvas p-4">
              <div>
                <label
                  htmlFor="feedback-category"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Kategori Masukan
                </label>
                <select
                  id="feedback-category"
                  value={category}
                  onChange={(e) =>
                    setCategory(e.target.value as FeedbackCategory)
                  }
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                >
                  {CATEGORY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="feedback-comment"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Catatan Tambahan (Opsional, maksimal 500 karakter)
                </label>
                <textarea
                  id="feedback-comment"
                  rows={2}
                  maxLength={500}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Contoh: Penjelasan sudah jelas, namun tautan rujukan bisa diperbanyak."
                  className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
                />
              </div>

              <div className="flex items-center justify-between gap-3">
                <span className="text-[11px] text-slate-500">
                  {comment.length}/500 karakter
                </span>
                <button
                  type="submit"
                  disabled={isPending}
                  className="rounded-full bg-brand-600 px-5 py-2 text-xs font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isPending ? "Mengirim..." : "Kirim Masukan"}
                </button>
              </div>
            </div>
          )}

          {validationError && (
            <p role="alert" className="text-xs font-medium text-rose-700">
              {validationError}
            </p>
          )}

          {isError && (
            <p role="alert" className="text-xs font-medium text-rose-700">
              {error instanceof Error
                ? error.message
                : "Gagal mengirim masukan. Silakan coba lagi."}
            </p>
          )}
        </form>
      )}
    </Card>
  );
}
