import type { Metadata } from "next";
import Link from "next/link";
import React from "react";
import "./globals.css";
import { AppQueryProvider } from "@/components/providers/query-provider";
import { MedicalDisclaimerBanner } from "@/components/layout/medical-disclaimer-banner";

export const metadata: Metadata = {
  title: "VeriMed — Verify Health. Trust Evidence.",
  description:
    "Platform kecerdasan bukti dan verifikasi klaim kesehatan berbasis bukti ilmiah untuk masyarakat Indonesia (SDG 3).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="min-h-screen flex flex-col">
        <MedicalDisclaimerBanner />
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-4">
            <Link href="/" className="flex items-center gap-3">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-brand-700 text-sm font-bold text-white">
                VM
              </span>
              <div>
                <span className="text-lg font-bold tracking-tight text-slate-900">
                  VeriMed
                </span>
                <span className="ml-2 rounded bg-teal-100 px-2 py-0.5 text-xs font-medium text-teal-800">
                  MVP
                </span>
              </div>
            </Link>
            <nav aria-label="Navigasi Utama" className="flex items-center gap-5">
              <Link
                href="/"
                className="text-sm font-medium text-slate-700 transition hover:text-brand-700"
              >
                Beranda
              </Link>
              <Link
                href="/verify"
                className="text-sm font-medium text-slate-700 transition hover:text-brand-700"
              >
                Verifikasi Klaim
              </Link>
              <Link
                href="/about"
                className="text-sm font-medium text-slate-700 transition hover:text-brand-700"
              >
                Metodologi
              </Link>
            </nav>
          </div>
        </header>
        <AppQueryProvider>
          <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
            {children}
          </main>
        </AppQueryProvider>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
          <div className="mx-auto max-w-5xl px-4">
            VeriMed (verimed-ai) — Platform Edukasi Verifikasi Klaim Kesehatan
            Berbasis Bukti. Mendukung Tujuan Pembangunan Berkelanjutan PBB (SDG
            3: Kehidupan Sehat dan Sejahtera).
          </div>
        </footer>
      </body>
    </html>
  );
}
