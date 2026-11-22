import React from "react";
import { CorpusExplorer } from "@/features/corpus/components/corpus-explorer";

export default function CorpusPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/80 bg-gradient-to-r from-white via-[#F7FAFF] to-[#EEF4FF] p-6 shadow-bento sm:p-7">
        <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
          <span className="h-2 w-2 rounded-full bg-brand-600" />
          Transparansi Sumber Rujukan
        </span>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Direktori Korpus Bukti Publik
        </h1>
        <p className="mt-1.5 max-w-3xl text-sm leading-relaxed text-slate-600">
          Telusuri dokumen kesehatan terkurasi dari Kemenkes RI, WHO, BPOM, dan
          korpus demonstrasi yang menjadi dasar penelusuran bukti VeriMed.
        </p>
      </section>

      <CorpusExplorer />
    </div>
  );
}
