import React from "react";

export default function AppLoading() {
  return (
    <div
      role="status"
      aria-label="Memuat halaman VeriMed"
      className="space-y-6"
    >
      <div className="h-36 animate-pulse rounded-3xl border border-white/80 bg-white/80 shadow-bento" />
      <div className="h-56 animate-pulse rounded-3xl border border-slate-200/70 bg-white/80 shadow-bento" />
    </div>
  );
}
