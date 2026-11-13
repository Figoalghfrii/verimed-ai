"use client";

import React from "react";
import { useBackendHealth } from "../api/use-backend-health";

export function BackendConnectivityCard() {
  const { data, isLoading, isError, error, refetch, isFetching } =
    useBackendHealth();

  const health = data?.data;
  const meta = data?.meta;

  return (
    <section
      aria-labelledby="system-status-heading"
      className="rounded-3xl border border-slate-200/75 bg-white p-6 shadow-bento sm:p-7"
    >
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5">
        <div>
          <h2
            id="system-status-heading"
            className="text-lg font-bold text-slate-900"
          >
            Status Konektivitas Sistem &amp; Basis Data Bukti
          </h2>
          <p className="mt-0.5 text-sm text-slate-600">
            Memverifikasi koneksi langsung ke endpoint{" "}
            <code className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-800">
              GET /api/v1/health
            </code>
          </p>
        </div>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:ring-offset-2 disabled:opacity-50"
        >
          {isFetching ? "Memeriksa..." : "Periksa Ulang Koneksi"}
        </button>
      </div>

      {isLoading && (
        <div
          role="status"
          className="mt-5 rounded-2xl bg-canvas p-4 text-sm text-slate-700"
        >
          Menghubungi layanan backend VeriMed API...
        </div>
      )}

      {isError && (
        <div
          role="alert"
          className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900"
        >
          <p className="font-semibold">Gagal terhubung ke Backend API</p>
          <p className="mt-1">
            {error instanceof Error
              ? error.message
              : "Pastikan server FastAPI berjalan di port 8000."}
          </p>
        </div>
      )}

      {health && (
        <div className="mt-5 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Status Layanan API
              </span>
              <div className="mt-1.5 flex items-center gap-2">
                <span
                  className={`inline-block h-2.5 w-2.5 rounded-full ${
                    health.status === "healthy"
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                  }`}
                />
                <span className="text-base font-bold text-slate-900">
                  {health.status === "healthy"
                    ? "Aktif (Healthy)"
                    : "Terdegradasi (Degraded)"}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-600">
                {health.service} v{health.version} ({health.environment})
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                PostgreSQL + pgvector
              </span>
              <div className="mt-1.5 flex items-center gap-2">
                <span
                  className={`inline-block h-2.5 w-2.5 rounded-full ${
                    health.database.status === "connected" &&
                    health.database.pgvector_enabled
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                  }`}
                />
                <span className="text-base font-bold text-slate-900">
                  {health.database.status === "connected"
                    ? "Terhubung"
                    : "Belum Terhubung"}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-600">
                pgvector:{" "}
                {health.database.pgvector_enabled ? "Aktif" : "Tidak Aktif"}
                {health.database.latency_ms !== null
                  ? ` • ${health.database.latency_ms} ms`
                  : ""}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200/70 bg-canvas p-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Mode Penyedia AI
              </span>
              <div className="mt-1.5">
                <span className="inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-900">
                  {health.ai_provider.toUpperCase()}
                  {meta?.is_demonstration ? " (Mode Demonstrasi)" : ""}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-600">
                API Versi: {meta?.api_version ?? "v1"}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-brand-100 bg-brand-50/70 p-4 text-xs leading-relaxed text-slate-700">
            <strong className="text-slate-900">Penafian Medis:</strong>{" "}
            {health.disclaimer}
          </div>
        </div>
      )}
    </section>
  );
}
