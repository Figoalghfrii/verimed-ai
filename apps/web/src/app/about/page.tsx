import React from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";

const PIPELINE_STEPS = [
  {
    step: "1. Validasi Input & Gerbang Darurat Medis",
    desc: "Memeriksa batas panjang input, membersihkan karakter berbahaya, dan mendeteksi gejala gawat darurat untuk segera mengarahkan pengguna ke layanan darurat 119 / IGD.",
  },
  {
    step: "2. Ekstraksi Klaim & Normalisasi Kueri",
    desc: "Memecah teks panjang menjadi klaim atomik yang dapat diverifikasi dan menormalisasi istilah kesehatan sehari-hari ke istilah medis terstandar.",
  },
  {
    step: "3. Pencarian Bukti Hibrida & Reranking",
    desc: "Menggabungkan pencarian kata kunci (tsvector) dan pencarian makna semantik (pgvector) lalu menyaring potongan bukti menggunakan cross-encoder.",
  },
  {
    step: "4. Penilaian Bukti & Mekanisme Abstain",
    desc: "Menetapkan label Didukung Bukti, Bertentangan dengan Bukti, Bukti Beragam, atau Bukti Tidak Cukup apabila relevansi bukti berada di bawah ambang minimum.",
  },
  {
    step: "5. Penjelasan Tergrounding & Validasi Sitasi",
    desc: "Mengisolasi teks bukti di dalam pembatas data tak tepercaya untuk mencegah prompt injection dan memverifikasi setiap nomor sitasi secara terprogram.",
  },
];

export default function AboutPage() {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <span className="inline-flex items-center rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800 ring-1 ring-inset ring-teal-600/20">
          Metodologi &amp; Transparansi AI
        </span>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Tentang VeriMed &amp; Metodologi Verifikasi
        </h1>
        <p className="max-w-3xl text-sm leading-relaxed text-slate-600">
          VeriMed (<em>Verify Health. Trust Evidence.</em>) adalah platform
          edukasi literasi kesehatan publik yang selaras dengan Tujuan
          Pembangunan Berkelanjutan PBB (<strong>SDG 3</strong>: Kehidupan Sehat
          dan Sejahtera).
        </p>
      </section>

      <Card as="section" ariaLabelledBy="pipeline-heading" className="space-y-4">
        <h2
          id="pipeline-heading"
          className="text-lg font-semibold text-slate-900"
        >
          Alur Pipeline Verifikasi Bukti
        </h2>
        <div className="space-y-3">
          {PIPELINE_STEPS.map((item) => (
            <div
              key={item.step}
              className="rounded-lg border border-slate-200 bg-slate-50/60 p-4"
            >
              <h3 className="text-sm font-semibold text-slate-900">
                {item.step}
              </h3>
              <p className="mt-1 text-sm text-slate-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card as="section" ariaLabelledBy="limits-heading" className="space-y-3">
        <h2
          id="limits-heading"
          className="text-lg font-semibold text-slate-900"
        >
          Batasan Sistem &amp; Komitmen Keselamatan
        </h2>
        <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-slate-700">
          <li>
            <strong>Bukan Alat Diagnosis Medis:</strong> VeriMed tidak menilai
            kondisi medis pribadi, hasil laboratorium, ataupun meresepkan obat.
          </li>
          <li>
            <strong>Label Menggambarkan Bukti yang Ditemukan:</strong> Label
            seperti <em>Didukung Bukti</em> atau <em>Bertentangan</em> merujuk
            pada konsistensi terhadap korpus bukti terindeks, bukan kebenaran
            medis mutlak.
          </li>
          <li>
            <strong>Status MVP Saat Ini:</strong> Pada fase pengembangan ini,
            pipeline berjalan dengan penyedia data simulasi deterministik (
            <code className="rounded bg-slate-100 px-1 py-0.5 font-mono text-xs">
              AI_PROVIDER=mock
            </code>
            ) sebelum pengindeksan korpus medis produksi.
          </li>
        </ul>
        <div className="pt-2">
          <Link
            href="/verify"
            className="inline-flex items-center rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            Coba Verifikasi Klaim Sekarang
          </Link>
        </div>
      </Card>
    </div>
  );
}
