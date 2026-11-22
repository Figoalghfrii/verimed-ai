import Link from "next/link";
import React from "react";
import { Card } from "@/components/ui/card";
import { FeedbackStatsCard } from "@/features/verification/components/feedback-stats-card";

const PIPELINE_STEPS = [
  {
    num: "01",
    step: "Validasi Input & Gerbang Darurat Medis",
    desc: "Memeriksa batas panjang input, membersihkan karakter berbahaya, dan mendeteksi gejala gawat darurat untuk segera mengarahkan pengguna ke layanan darurat 119 / IGD.",
  },
  {
    num: "02",
    step: "Ekstraksi Klaim & Normalisasi Kueri",
    desc: "Memecah teks panjang menjadi klaim atomik yang dapat diverifikasi dan menormalisasi istilah kesehatan sehari-hari ke istilah medis terstandar.",
  },
  {
    num: "03",
    step: "Pencarian Bukti Hibrida & Reranking",
    desc: "Menggabungkan pencarian kata kunci (tsvector) dan pencarian makna semantik (pgvector) lalu menyaring potongan bukti menggunakan cross-encoder.",
  },
  {
    num: "04",
    step: "Penilaian Bukti & Mekanisme Abstain",
    desc: "Menetapkan label Didukung Bukti, Bertentangan dengan Bukti, Bukti Beragam, atau Bukti Tidak Cukup apabila relevansi bukti berada di bawah ambang minimum.",
  },
  {
    num: "05",
    step: "Penjelasan Tergrounding & Validasi Sitasi",
    desc: "Mengisolasi teks bukti di dalam pembatas data tak tepercaya untuk mencegah prompt injection dan memverifikasi setiap nomor sitasi secara terprogram.",
  },
];

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/80 bg-gradient-to-r from-white via-[#F7FAFF] to-[#EEF4FF] p-6 shadow-bento sm:p-7">
        <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
          <span className="h-2 w-2 rounded-full bg-brand-600" />
          Metodologi &amp; Transparansi AI
        </span>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Tentang VeriMed &amp; Metodologi Verifikasi
        </h1>
        <p className="mt-1.5 max-w-3xl text-sm leading-relaxed text-slate-600">
          VeriMed (<em>Verify Health. Trust Evidence.</em>) adalah platform
          edukasi literasi kesehatan publik yang selaras dengan Tujuan
          Pembangunan Berkelanjutan PBB (<strong>SDG 3</strong>: Kehidupan Sehat
          dan Sejahtera).
        </p>
      </section>

      <Card as="section" ariaLabelledBy="pipeline-heading" className="space-y-4 sm:p-7">
        <h2
          id="pipeline-heading"
          className="text-lg font-bold text-slate-900"
        >
          Alur Pipeline Verifikasi Bukti
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {PIPELINE_STEPS.map((item) => (
            <div
              key={item.num}
              className="rounded-2xl border border-slate-200/70 bg-canvas p-5"
            >
              <span className="inline-flex h-7 items-center rounded-full bg-brand-600 px-3 text-xs font-bold text-white">
                Tahap {item.num}
              </span>
              <h3 className="mt-2.5 text-sm font-bold text-slate-900">
                {item.step}
              </h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-600">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </Card>

      <Card as="section" ariaLabelledBy="limits-heading" className="space-y-4 sm:p-7">
        <h2
          id="limits-heading"
          className="text-lg font-bold text-slate-900"
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
            <strong>Mode Operasional Fleksibel:</strong> VeriMed mendukung mode
            demonstrasi deterministik (
            <code className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-xs">
              AI_PROVIDER=mock
            </code>
            ), mode <em>hybrid retrieval</em> lokal berbasis PostgreSQL{" "}
            <code className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-xs">
              pgvector
            </code>{" "}
            +{" "}
            <code className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-xs">
              tsvector
            </code>{" "}
            (
            <code className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-xs">
              AI_PROVIDER=hybrid
            </code>
            ), serta integrasi model bahasa eksternal tergrounding dengan
            validasi sitasi terprogram (
            <code className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-xs">
              AI_PROVIDER=configurable
            </code>
            ).
          </li>
        </ul>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link
            href="/verify"
            className="inline-flex items-center gap-2 rounded-full bg-brand-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
          >
            <span>Coba Verifikasi Klaim Sekarang</span>
            <span aria-hidden="true">&rarr;</span>
          </Link>
          <Link
            href="/corpus"
            className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-6 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:bg-brand-50"
          >
            <span>Lihat Direktori Korpus Bukti</span>
          </Link>
        </div>
      </Card>

      <FeedbackStatsCard />
    </div>
  );
}
