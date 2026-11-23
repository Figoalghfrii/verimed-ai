"use client";

import Link from "next/link";
import React from "react";

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <section
      role="alert"
      className="mx-auto max-w-2xl rounded-3xl border border-rose-200 bg-white p-8 text-center shadow-bento"
    >
      <span className="inline-flex rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-800">
        Gangguan Sementara
      </span>
      <h1 className="mt-3 text-xl font-bold text-slate-900">
        Terjadi kesalahan saat memuat halaman VeriMed
      </h1>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">
        Silakan muat ulang tampilan ini atau kembali ke halaman utama untuk
        melanjutkan verifikasi klaim kesehatan.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <button
          type="button"
          onClick={() => reset()}
          className="rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
        >
          Coba Muat Ulang
        </button>
        <Link
          href="/"
          className="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Kembali ke Ringkasan
        </Link>
      </div>
    </section>
  );
}
