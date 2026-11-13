import React from "react";
import { Badge } from "@/components/ui/badge";
import { EvidenceSourceItem } from "../schemas/verification-schema";

const STANCE_CONFIG: Record<
  EvidenceSourceItem["stance"],
  { label: string; variant: "success" | "danger" | "info" }
> = {
  SUPPORTING: { label: "Mendukung", variant: "success" },
  CONTRADICTING: { label: "Membantah", variant: "danger" },
  CONTEXTUAL: { label: "Kontekstual", variant: "info" },
};

export function EvidenceSourceCard({ source }: { source: EvidenceSourceItem }) {
  const stanceInfo = STANCE_CONFIG[source.stance];

  return (
    <article className="rounded-2xl border border-slate-200/80 bg-canvas p-5 transition hover:border-brand-200">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-slate-900 px-2.5 py-0.5 font-mono text-xs font-semibold text-white">
            {source.citation_key}
          </span>
          <Badge variant={stanceInfo.variant}>{stanceInfo.label}</Badge>
          {source.is_synthetic_demo && (
            <Badge variant="warning">Data Simulasi Demo</Badge>
          )}
        </div>
        <span className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 shadow-sm">
          Relevansi: {Math.round(source.relevance_score * 100)}%
        </span>
      </div>

      <h4 className="mt-3 text-sm font-bold text-slate-900">{source.title}</h4>
      <p className="mt-0.5 text-xs text-slate-500">
        {source.source_name}
        {source.publication_date
          ? ` • Tanggal: ${source.publication_date}`
          : ""}
      </p>

      <blockquote className="mt-3 rounded-xl border-l-4 border-brand-500 bg-white p-3.5 text-sm leading-relaxed text-slate-700">
        {source.excerpt}
      </blockquote>

      <p className="mt-2.5 text-xs text-slate-500 break-all">
        Referensi sumber: <span className="font-mono">{source.source_url}</span>
      </p>
    </article>
  );
}
