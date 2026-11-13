import Link from "next/link";
import React from "react";
import { BackendConnectivityCard } from "@/features/system-status/components/backend-connectivity-card";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <span className="inline-flex items-center rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800 ring-1 ring-inset ring-teal-600/20">
          SDG 3 — Kehidupan Sehat dan Sejahtera
        </span>
        <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
          VeriMed: Verifikasi Klaim Kesehatan Berbasis Bukti Ilmiah
        </h1>
        <p className="mt-3 max-w-3xl text-base leading-relaxed text-slate-600">
          VeriMed membantu masyarakat Indonesia mengevaluasi klaim kesehatan
          yang beredar di media sosial dan aplikasi pesan melalui pencarian
          literatur medis tepercaya, penilaian bukti yang terkalibrasi, serta
          komunikasi ketidakpastian ilmiah yang transparan.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/verify"
            className="inline-flex items-center rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            Periksa Klaim Kesehatan
          </Link>
          <Link
            href="/about"
            className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Pelajari Metodologi
          </Link>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 p-3.5">
            <p className="text-xs font-semibold text-emerald-900">
              Didukung Bukti
            </p>
            <p className="mt-1 text-xs text-emerald-800">
              Konsisten dengan bukti ilmiah tepercaya yang ditemukan.
            </p>
          </div>
          <div className="rounded-lg border border-rose-200 bg-rose-50/60 p-3.5">
            <p className="text-xs font-semibold text-rose-900">
              Bertentangan dengan Bukti
            </p>
            <p className="mt-1 text-xs text-rose-800">
              Tidak sesuai atau dibantah oleh bukti ilmiah yang tersedia.
            </p>
          </div>
          <div className="rounded-lg border border-amber-200 bg-amber-50/60 p-3.5">
            <p className="text-xs font-semibold text-amber-900">
              Bukti Beragam
            </p>
            <p className="mt-1 text-xs text-amber-800">
              Studi ilmiah menunjukkan hasil yang beragam atau bergantung
              konteks.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-100 p-3.5">
            <p className="text-xs font-semibold text-slate-900">
              Bukti Tidak Cukup
            </p>
            <p className="mt-1 text-xs text-slate-700">
              Sistem menahan diri (abstain) ketika bukti ilmiah belum memadai.
            </p>
          </div>
        </div>
      </section>

      <BackendConnectivityCard />
    </div>
  );
}
