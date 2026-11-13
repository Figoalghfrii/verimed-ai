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
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h2
            id="system-status-heading"
            className="text-lg font-semibold text-slate-900"
          >
            Status Konektivitas Sistem &amp; Basis Data Bukti
          </h2>
          <p className="text-sm text-slate-600">
            Memverifikasi koneksi langsung ke endpoint{" "}
            <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-800">
              GET /api/v1/health
            </code>
          </p>
        </div>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center rounded-lg border border-brand-600 bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:ring-offset-2 disabled:opacity-50"
        >
          {isFetching ? "Memeriksa..." : "Periksa Ulang Koneksi"}
        </button>
      </div>

      {isLoading && (
        <div
          role="status"
          className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-700"
        >
          Menghubungi layanan backend VeriMed API...
        </div>
      )}

      {isError && (
        <div
          role="alert"
          className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900"
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
        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
                Status Layanan API
              </span>
              <div className="mt-1 flex items-center gap-2">
                <span
                  className={`inline-block h-2.5 w-2.5 rounded-full ${
                    health.status === "healthy"
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                  }`}
                />
                <span className="text-base font-semibold text-slate-900">
                  {health.status === "healthy"
                    ? "Aktif (Healthy)"
                    : "Terdegradasi (Degraded)"}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-600">
                {health.service} v{health.version} ({health.environment})
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
                PostgreSQL + pgvector
              </span>
              <div className="mt-1 flex items-center gap-2">
                <span
                  className={`inline-block h-2.5 w-2.5 rounded-full ${
                    health.database.status === "connected" &&
                    health.database.pgvector_enabled
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                  }`}
                />
                <span className="text-base font-semibold text-slate-900">
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

            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
                Mode Penyedia AI
              </span>
              <div className="mt-1">
                <span className="inline-flex items-center rounded-md bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-900">
                  {health.ai_provider.toUpperCase()}
                  {meta?.is_demonstration ? " (Mode Demonstrasi)" : ""}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-600">
                API Versi: {meta?.api_version ?? "v1"}
              </p>
            </div>
          </div>

          <div className="rounded-lg border border-teal-200 bg-teal-50 p-3.5 text-xs text-teal-950">
            <strong>Penafian Medis:</strong> {health.disclaimer}
          </div>
        </div>
      )}
    </section>
  );
}
