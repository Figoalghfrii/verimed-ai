"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { useFeedbackStats } from "../api/use-feedback-stats";

export function FeedbackStatsCard() {
  const { data, isLoading, isError } = useFeedbackStats();
  const stats = data?.data;

  return (
    <Card as="section" ariaLabelledBy="feedback-stats-heading" className="space-y-4 sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2
            id="feedback-stats-heading"
            className="text-lg font-bold text-slate-900"
          >
            Ringkasan Umpan Balik Kejelasan Pengguna
          </h2>
          <p className="mt-0.5 text-xs text-slate-600">
            Agregasi anonim dari{" "}
            <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">
              GET /api/v1/feedback/stats
            </code>{" "}
            tanpa menampilkan komentar teks mentah atau data pribadi.
          </p>
        </div>
      </div>

      {isLoading && (
        <p role="status" className="text-sm text-slate-600">
          Memuat statistik umpan balik pengguna...
        </p>
      )}

      {isError && (
        <p className="text-xs text-slate-500">
          Statistik umpan balik tidak tersedia saat backend offline.
        </p>
      )}

      {stats && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
            <span className="text-xs font-medium text-slate-500">
              Total Penilaian
            </span>
            <p className="mt-1 text-2xl font-bold tabular-nums text-slate-900">
              {stats.total_count}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
            <span className="text-xs font-medium text-slate-500">
              Dinilai Membantu
            </span>
            <p className="mt-1 text-2xl font-bold tabular-nums text-emerald-700">
              {stats.helpful_count}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
            <span className="text-xs font-medium text-slate-500">
              Tingkat Kejelasan
            </span>
            <p className="mt-1 text-2xl font-bold tabular-nums text-brand-700">
              {Math.round(stats.helpful_rate * 100)}%
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}
