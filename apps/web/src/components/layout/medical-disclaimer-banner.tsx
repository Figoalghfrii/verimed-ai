import React from "react";

export function MedicalDisclaimerBanner() {
  return (
    <div
      role="region"
      aria-label="Penafian Medis"
      className="border-b border-brand-100 bg-white/80 px-4 py-2 text-center text-xs text-slate-600"
    >
      <span className="mr-1.5 inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-semibold text-amber-900">
        Edukasi Non-Diagnostik
      </span>
      VeriMed adalah platform verifikasi klaim kesehatan berbasis bukti ilmiah,{" "}
      <strong className="text-slate-800">bukan</strong> alat diagnosis medis.
      Dalam kondisi darurat medis, hubungi{" "}
      <strong className="text-rose-700">119</strong> atau kunjungi IGD
      terdekat.
    </div>
  );
}
