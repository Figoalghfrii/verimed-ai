import Link from "next/link";
import React from "react";

export default function NotFoundPage() {
  return (
    <section className="mx-auto max-w-2xl rounded-3xl border border-slate-200/80 bg-white p-8 text-center shadow-bento">
      <span className="inline-flex rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
        404 • Halaman Tidak Ditemukan
      </span>
      <h1 className="mt-3 text-2xl font-bold text-slate-900">
        Halaman yang Anda cari tidak tersedia
      </h1>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">
        Periksa kembali alamat URL atau gunakan pintasan berikut untuk
        memeriksa klaim kesehatan dan menelusuri korpus bukti publik VeriMed.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Link
          href="/verify"
          className="rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
        >
          Buka Verifikasi Klaim
        </Link>
        <Link
          href="/"
          className="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Ke Beranda Ringkasan
        </Link>
      </div>
    </section>
  );
}
