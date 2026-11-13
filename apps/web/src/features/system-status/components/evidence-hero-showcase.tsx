import Link from "next/link";
import React from "react";

const HEATMAP_OPACITIES = [
  0.2, 0.35, 0.6, 0.9, 0.45, 0.75, 0.55, 0.85,
  0.4, 0.8, 0.95, 0.5, 0.3, 0.65, 0.9, 0.7,
  0.6, 0.5, 0.35, 0.75, 0.85, 0.4, 0.6, 0.95,
  0.3, 0.65, 0.8, 0.45, 0.55, 0.9, 0.7, 0.5,
];

const TICK_BARS = [
  { h: 14, color: "bg-slate-300" },
  { h: 24, color: "bg-brand-500" },
  { h: 18, color: "bg-emerald-500" },
  { h: 28, color: "bg-slate-300" },
  { h: 16, color: "bg-brand-600" },
  { h: 22, color: "bg-slate-300" },
  { h: 30, color: "bg-emerald-500" },
  { h: 20, color: "bg-brand-500" },
  { h: 15, color: "bg-slate-300" },
  { h: 26, color: "bg-brand-600" },
  { h: 19, color: "bg-slate-300" },
  { h: 24, color: "bg-brand-500" },
];

export function EvidenceHeroShowcase() {
  return (
    <section
      aria-labelledby="hero-heading"
      className="grid grid-cols-1 gap-6 lg:grid-cols-12 lg:items-stretch"
    >
      {/* Left Focal Evidence Canvas (Inspired by Mediva frosted-glass + gauge layout) */}
      <div className="relative flex flex-col justify-between overflow-hidden rounded-[28px] border border-white/80 bg-gradient-to-br from-white via-[#F7FAFF] to-[#EEF4FF] p-6 shadow-bento sm:p-8 lg:col-span-6">
        <div className="relative z-10 space-y-3">
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3.5 py-1 text-xs font-semibold text-brand-700">
            <span className="h-2 w-2 rounded-full bg-brand-600" />
            Verify Health. Trust Evidence.
          </span>
          <h1
            id="hero-heading"
            className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl"
          >
            Verifikasi Klaim Kesehatan Berbasis Bukti Ilmiah
          </h1>
          <p className="max-w-xl text-sm leading-relaxed text-slate-600">
            Evaluasi klaim kesehatan dari media sosial dan pesan berantai dengan
            penilaian terkalibrasi, sitasi terverifikasi, dan transparansi
            ketidakpastian ilmiah.
          </p>
        </div>

        {/* Visual Core + Curved Gauge + Frosted Floating Verdict Cards */}
        <div className="relative my-6 flex min-h-[290px] items-center justify-center">
          {/* Left Curved Calibration Scale */}
          <div
            aria-hidden="true"
            className="absolute left-0 top-4 bottom-4 hidden w-14 flex-col justify-between py-2 text-[10px] font-semibold text-slate-400 sm:flex"
          >
            <div className="flex items-center gap-1.5">
              <span className="h-px w-4 bg-slate-300" />
              <span>95%</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-px w-3 bg-slate-200" />
            </div>
            <div className="flex items-center gap-1.5 text-brand-600">
              <span className="h-0.5 w-6 rounded-full bg-brand-600" />
              <span>70%</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-px w-3 bg-slate-200" />
            </div>
            <div className="flex items-center gap-1.5 text-amber-700">
              <span className="h-0.5 w-5 rounded-full bg-amber-500" />
              <span>35%</span>
            </div>
          </div>

          {/* Central Glowing Evidence Core SVG */}
          <div className="relative flex items-center justify-center">
            <div
              aria-hidden="true"
              className="h-52 w-52 rounded-full bg-gradient-to-tr from-rose-200/70 via-brand-100/80 to-sky-100/70 blur-2xl"
            />
            <svg
              aria-hidden="true"
              viewBox="0 0 240 240"
              className="absolute h-52 w-52 drop-shadow-sm"
            >
              <defs>
                <radialGradient id="coreGlow" cx="45%" cy="38%" r="60%">
                  <stop offset="0%" stopColor="#FB7185" />
                  <stop offset="55%" stopColor="#E11D48" />
                  <stop offset="100%" stopColor="#9F1239" />
                </radialGradient>
                <linearGradient id="shieldOverlay" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#1D7DFA" stopOpacity="0.15" />
                </linearGradient>
              </defs>
              {/* Orbital Ring */}
              <ellipse
                cx="120"
                cy="196"
                rx="78"
                ry="16"
                fill="none"
                stroke="#93C5FD"
                strokeWidth="1.6"
              />
              {/* Soft 3D Medical Shield / Heart Core */}
              <path
                d="M120 42C94 42 74 60 74 86c0 39 46 72 46 72s46-33 46-72c0-26-20-44-46-44z"
                fill="url(#coreGlow)"
              />
              <path
                d="M120 50C98 50 82 65 82 87c0 32 38 60 38 60s38-28 38-60c0-22-16-37-38-37z"
                fill="url(#shieldOverlay)"
              />
              {/* Crisp Evidence Pulse Line inside Core */}
              <path
                d="M84 96h18l8-17 12 31 9-18h25"
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="3.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            {/* Top-Left Floating Glass Card */}
            <div className="absolute -left-6 -top-2 w-44 rounded-2xl border border-white/90 bg-white/80 p-3 shadow-glass backdrop-blur-md sm:-left-16">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-emerald-700">
                  Didukung Bukti
                </span>
                <span className="h-2.5 w-2.5 rounded-full border-2 border-white bg-emerald-500 shadow" />
              </div>
              <p className="mt-1 text-base font-bold text-slate-900">
                Konsisten
              </p>
              <p className="text-[11px] text-slate-500">
                Sesuai korpus terkurasi
              </p>
            </div>

            {/* Top-Right Floating Glass Card */}
            <div className="absolute -right-6 top-6 w-44 rounded-2xl border border-white/90 bg-white/80 p-3 shadow-glass backdrop-blur-md sm:-right-16">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-rose-700">
                  Bertentangan
                </span>
                <span className="h-2.5 w-2.5 rounded-full border-2 border-white bg-rose-500 shadow" />
              </div>
              <p className="mt-1 text-base font-bold text-slate-900">
                Dibantah
              </p>
              <p className="text-[11px] text-slate-500">
                Tidak sejalan bukti ilmiah
              </p>
            </div>

            {/* Bottom-Left Floating Glass Card */}
            <div className="absolute -left-4 bottom-2 w-44 rounded-2xl border border-white/90 bg-white/80 p-3 shadow-glass backdrop-blur-md sm:-left-14">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-amber-700">
                  Bukti Beragam
                </span>
                <span className="h-2.5 w-2.5 rounded-full border-2 border-white bg-amber-500 shadow" />
              </div>
              <p className="mt-1 text-base font-bold text-slate-900">
                Kontekstual
              </p>
              <p className="text-[11px] text-slate-500">
                Temuan studi bervariasi
              </p>
            </div>

            {/* Bottom-Right Floating Glass Card */}
            <div className="absolute -right-4 -bottom-2 w-44 rounded-2xl border border-white/90 bg-white/80 p-3 shadow-glass backdrop-blur-md sm:-right-14">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-700">
                  Bukti Tidak Cukup
                </span>
                <span className="h-2.5 w-2.5 rounded-full border-2 border-white bg-brand-600 shadow" />
              </div>
              <p className="mt-1 text-base font-bold text-slate-900">
                Abstain
              </p>
              <p className="text-[11px] text-slate-500">
                Menahan diri bila minim
              </p>
            </div>
          </div>
        </div>

        {/* Action Pills */}
        <div className="relative z-10 flex flex-wrap items-center gap-3 pt-2">
          <Link
            href="/verify"
            className="inline-flex items-center gap-2 rounded-full bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:ring-offset-2"
          >
            <span>Periksa Klaim Kesehatan</span>
            <span aria-hidden="true">&rarr;</span>
          </Link>
          <Link
            href="/about"
            className="inline-flex items-center rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Pelajari Metodologi
          </Link>
        </div>
      </div>

      {/* Right 2-Column Bento Intelligence Grid (Styled after Mediva right metric tiles) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:col-span-6">
        {/* Card 1: Pipeline Stages Tick Bars */}
        <article className="flex flex-col justify-between rounded-3xl border border-slate-200/75 bg-white p-5 shadow-bento">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-xs font-medium text-slate-500">
                Alur Pipeline AI
              </p>
              <h2 className="mt-0.5 text-sm font-bold text-slate-900">
                Verifikasi Terstruktur
              </h2>
            </div>
            <span className="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-semibold text-brand-700">
              8 Tahap
            </span>
          </div>
          <div
            aria-hidden="true"
            className="mt-5 flex h-12 items-end justify-between gap-1.5 px-1"
          >
            {TICK_BARS.map((bar, idx) => (
              <span
                key={idx}
                style={{ height: `${bar.h}px` }}
                className={`w-1.5 rounded-full ${bar.color}`}
              />
            ))}
          </div>
          <p className="mt-3 text-xs text-slate-500">
            Ekstraksi, normalisasi, pencarian, hingga validasi sitasi.
          </p>
        </article>

        {/* Card 2: Emergency 119 ECG Waveform */}
        <article className="flex flex-col justify-between rounded-3xl border border-slate-200/75 bg-white p-5 shadow-bento">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-xs font-medium text-slate-500">
                Keselamatan Medis
              </p>
              <h2 className="mt-0.5 text-sm font-bold text-slate-900">
                Gerbang Darurat 119
              </h2>
            </div>
            <span className="rounded-full bg-rose-50 px-2.5 py-1 text-[11px] font-semibold text-rose-700">
              Siaga
            </span>
          </div>
          <svg
            aria-hidden="true"
            viewBox="0 0 180 48"
            className="mt-4 h-12 w-full"
          >
            <path
              d="M2 26h28l7-10 8 22 9-30 8 34 7-16h34l6-9 7 18 8-24 7 28 6-13h43"
              fill="none"
              stroke="#1D7DFA"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="mt-3 text-xs text-slate-500">
            Deteksi gejala darurat langsung diarahkan ke 119 / IGD.
          </p>
        </article>

        {/* Card 3: 8x4 Blue Matrix (Evidence Integrity & Zero Fabrication) */}
        <article className="flex flex-col justify-between rounded-3xl border border-slate-200/75 bg-white p-5 shadow-bento">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-bold text-slate-900">
              Integritas Bukti
            </h2>
            <span className="text-xs font-medium text-slate-500">
              Anti-Halusinasi
            </span>
          </div>
          <div
            aria-hidden="true"
            className="mt-4 grid grid-cols-8 gap-1.5"
          >
            {HEATMAP_OPACITIES.map((opacity, idx) => (
              <span
                key={idx}
                style={{ opacity }}
                className="h-4 rounded-[5px] bg-brand-600"
              />
            ))}
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              0
            </span>
            <span className="text-xs font-medium text-slate-500">
              Toleransi sitasi palsu
            </span>
          </div>
        </article>

        {/* Card 4: Step Area Chart (Abstention Threshold) */}
        <article className="flex flex-col justify-between rounded-3xl border border-slate-200/75 bg-white p-5 shadow-bento">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-bold text-slate-900">
              Ambang Abstain
            </h2>
            <span className="text-xs font-medium text-slate-500">
              Kalibrasi
            </span>
          </div>
          <svg
            aria-hidden="true"
            viewBox="0 0 180 68"
            className="mt-3 h-16 w-full"
          >
            <defs>
              <linearGradient id="stepFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1D7DFA" stopOpacity="0.22" />
                <stop offset="100%" stopColor="#1D7DFA" stopOpacity="0.02" />
              </linearGradient>
            </defs>
            <path
              d="M4 54 H34 V32 H68 V18 H102 V38 H136 V14 H172 V64 H4 Z"
              fill="url(#stepFill)"
            />
            <path
              d="M4 54 H34 V32 H68 V18 H102 V38 H136 V14 H172"
              fill="none"
              stroke="#1D7DFA"
              strokeWidth="2.4"
              strokeLinejoin="round"
            />
            <circle cx="172" cy="14" r="4" fill="#1D7DFA" />
          </svg>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              35%
            </span>
            <span className="text-xs font-medium text-slate-500">
              Skor relevansi minimum
            </span>
          </div>
        </article>

        {/* Card 5: Programmatic Citation Validation */}
        <article className="flex flex-col justify-between rounded-3xl border border-slate-200/75 bg-white p-5 shadow-bento">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-bold text-slate-900">
              Validasi Sitasi
            </h2>
            <span className="text-xs font-medium text-slate-500">
              Terprogram
            </span>
          </div>
          <svg
            aria-hidden="true"
            viewBox="0 0 180 56"
            className="mt-3 h-14 w-full"
          >
            <path
              d="M4 34 H32 V16 H52 V46 H74 V10 H96 V42 H118 V24 H142 V34 H176"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="3"
              strokeLinejoin="round"
            />
            <path
              d="M96 42 H118 V24 H142"
              fill="none"
              stroke="#1D7DFA"
              strokeWidth="3.5"
              strokeLinejoin="round"
            />
          </svg>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              100%
            </span>
            <span className="text-xs font-medium text-slate-500">
              Pemetaan ke chunk bukti
            </span>
          </div>
        </article>

        {/* Card 6: Privacy by Default Capsule Ring */}
        <article className="flex flex-col justify-between rounded-3xl border border-slate-200/75 bg-white p-5 shadow-bento">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-bold text-slate-900">
              Privasi Pengguna
            </h2>
            <span className="text-xs font-medium text-slate-500">
              Default
            </span>
          </div>
          <div aria-hidden="true" className="my-3 flex items-center justify-center">
            <div className="relative h-14 w-full rounded-2xl border-4 border-slate-200 bg-slate-50/50">
              <div className="absolute inset-y-[-4px] left-6 right-[-4px] rounded-2xl border-4 border-brand-600" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              Privat
            </span>
            <span className="text-xs font-medium text-slate-500">
              Tanpa log payload sensitif
            </span>
          </div>
        </article>
      </div>
    </section>
  );
}
