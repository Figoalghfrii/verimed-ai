import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import { headers } from "next/headers";
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
  title: {
    default: "VeriMed — Verify Health. Trust Evidence.",
    template: "%s | VeriMed",
  },
  description:
    "Platform kecerdasan bukti dan verifikasi klaim kesehatan berbasis bukti ilmiah untuk masyarakat Indonesia (SDG 3).",
  keywords: [
    "VeriMed",
    "verifikasi klaim kesehatan",
    "literasi kesehatan",
    "fakta medis",
    "SDG 3",
  ],
  openGraph: {
    title: "VeriMed — Verify Health. Trust Evidence.",
    description:
      "Evaluasi klaim kesehatan dari media sosial dengan penilaian terkalibrasi, sitasi ilmiah, dan transparansi ketidakpastian.",
    locale: "id_ID",
    type: "website",
  },
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Reading request headers opts SSR into per-request CSP nonce propagation.
  const requestHeaders = await headers();
  const nonce = requestHeaders.get("x-nonce") ?? undefined;
  return (
    <html lang="id" className={plusJakartaSans.className} data-csp-nonce={nonce ? "1" : "0"}>
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
