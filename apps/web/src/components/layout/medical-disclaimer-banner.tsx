import React from "react";

export function MedicalDisclaimerBanner() {
  return (
    <div
      role="region"
      aria-label="Penafian Medis"
      className="border-b border-amber-200 bg-amber-50 px-4 py-2.5 text-center text-xs text-amber-950"
    >
      <strong>Informasi Penting:</strong> VeriMed adalah platform edukasi
      verifikasi klaim kesehatan berbasis bukti ilmiah, <strong>bukan</strong>{" "}
      alat diagnosis medis. Dalam kondisi darurat medis, segera hubungi{" "}
      <strong>119</strong> atau kunjungi IGD terdekat.
    </div>
  );
}
