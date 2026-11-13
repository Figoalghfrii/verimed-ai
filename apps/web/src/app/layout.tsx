import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import React from "react";
import "./globals.css";
import { MedicalDisclaimerBanner } from "@/components/layout/medical-disclaimer-banner";
import { TopNavbar } from "@/components/layout/top-navbar";
import { AppQueryProvider } from "@/components/providers/query-provider";

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

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
    <html lang="id" className={plusJakartaSans.className}>
      <body className="min-h-screen flex flex-col bg-canvas text-slate-900">
        <MedicalDisclaimerBanner />
        <TopNavbar />
        <AppQueryProvider>
          <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:py-8">
            {children}
          </main>
        </AppQueryProvider>
        <footer className="border-t border-slate-200/70 bg-white/80 py-6 text-center text-xs text-slate-500">
          <div className="mx-auto max-w-6xl px-4">
            VeriMed (verimed-ai) — Verify Health. Trust Evidence. Mendukung
            Tujuan Pembangunan Berkelanjutan PBB (SDG 3: Kehidupan Sehat dan
            Sejahtera).
          </div>
        </footer>
      </body>
    </html>
  );
}
