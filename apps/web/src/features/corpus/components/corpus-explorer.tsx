"use client";

import Link from "next/link";
import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { getSafeExternalUrl } from "@/lib/safe-url";
import { useEvidenceDocuments } from "../api/use-evidence-documents";

const PAGE_SIZE = 10;

const SOURCE_TYPE_FILTERS: Array<{ value: string; label: string }> = [
  { value: "", label: "Semua Jenis Sumber" },
  { value: "OFFICIAL_GUIDELINE", label: "Kemenkes RI" },
  { value: "WHO_FACT_SHEET", label: "WHO Fact Sheet" },
  { value: "WHO_GUIDANCE", label: "WHO Guidance" },
  { value: "BPOM_ADVISORY", label: "BPOM RI" },
  { value: "SYNTHETIC_DEMO_GUIDELINE", label: "Simulasi Demo" },
];

export function CorpusExplorer() {
  const [searchInput, setSearchInput] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [includeSynthetic, setIncludeSynthetic] = useState(true);
  const [offset, setOffset] = useState(0);

  const { data, isLoading, isError, error } = useEvidenceDocuments({
    q: appliedSearch,
    sourceType: sourceType || undefined,
    includeSynthetic,
    limit: PAGE_SIZE,
    offset,
  });

  const payload = data?.data;

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setOffset(0);
    setAppliedSearch(searchInput.trim());
  };

  return (
    <div className="space-y-6">
      <Card as="section" ariaLabelledBy="corpus-filter-heading" className="space-y-4">
        <h2
          id="corpus-filter-heading"
          className="text-base font-bold text-slate-900"
        >
          Cari &amp; Saring Sumber Bukti Terindeks
        </h2>

        <form
          onSubmit={handleSearchSubmit}
          className="flex flex-wrap items-center gap-3"
        >
          <label htmlFor="corpus-search-input" className="sr-only">
            Cari judul atau penerbit dokumen bukti
          </label>
          <input
            id="corpus-search-input"
            type="search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Cari judul atau lembaga (mis. Kemenkes, WHO, BPOM, campak)..."
            className="min-w-[240px] flex-1 rounded-full border border-slate-200 bg-canvas px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-200"
          />
          <button
            type="submit"
            className="rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
          >
            Cari Sumber
          </button>
          {appliedSearch && (
            <button
              type="button"
              onClick={() => {
                setOffset(0);
                setSearchInput("");
                setAppliedSearch("");
              }}
              className="rounded-full border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Reset
            </button>
          )}
        </form>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex flex-wrap gap-2">
            {SOURCE_TYPE_FILTERS.map((filter) => {
              const active = sourceType === filter.value;
              return (
                <button
                  key={filter.label}
                  type="button"
                  aria-pressed={active}
                  onClick={() => {
                    setOffset(0);
                    setSourceType(filter.value);
                  }}
                  className={`rounded-full border px-3.5 py-1.5 text-xs font-semibold transition ${
                    active
                      ? "border-brand-600 bg-brand-600 text-white"
                      : "border-slate-200 bg-white text-slate-700 hover:border-brand-300 hover:bg-brand-50"
                  }`}
                >
                  {filter.label}
                </button>
              );
            })}
          </div>

          <label className="inline-flex cursor-pointer items-center gap-2 text-xs font-medium text-slate-700">
            <input
              type="checkbox"
              checked={includeSynthetic}
              onChange={(e) => {
                setOffset(0);
                setIncludeSynthetic(e.target.checked);
              }}
              className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <span>Tampilkan juga dokumen simulasi demo</span>
          </label>
        </div>
      </Card>

      {isLoading && (
        <Card as="section" ariaLabelledBy="corpus-loading-heading">
          <p
            id="corpus-loading-heading"
            role="status"
            className="text-sm text-slate-600"
          >
            Memuat daftar dokumen korpus bukti...
          </p>
        </Card>
      )}

      {isError && (
        <div
          role="alert"
          className="rounded-3xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-900 shadow-bento"
        >
          <p className="font-bold">Gagal memuat direktori korpus bukti</p>
          <p className="mt-1">
            {error instanceof Error
              ? error.message
              : "Pastikan layanan backend FastAPI berjalan di port 8000."}
          </p>
        </div>
      )}

      {payload && !payload.database_connected && (
        <div
          role="note"
          className="rounded-3xl border border-amber-200 bg-amber-50/90 p-5 text-sm text-amber-950 shadow-bento"
        >
          <strong>Basis Data Tidak Terhubung:</strong> Layanan API berjalan
          dalam mode <em>stateless</em> tanpa PostgreSQL aktif. Jalankan{" "}
          <code className="rounded bg-amber-100 px-1.5 py-0.5 font-mono text-xs">
            docker compose up -d postgres
          </code>{" "}
          dan{" "}
          <code className="rounded bg-amber-100 px-1.5 py-0.5 font-mono text-xs">
            seed_demo_data.py --preset curated
          </code>{" "}
          untuk menampilkan daftar dokumen terindeks.
        </div>
      )}

      {payload && payload.database_connected && payload.items.length === 0 && (
        <Card as="section" ariaLabelledBy="corpus-empty-heading">
          <p id="corpus-empty-heading" className="text-sm text-slate-600">
            Tidak ada dokumen bukti yang cocok dengan filter pencarian saat ini.
          </p>
        </Card>
      )}

      {payload && payload.items.length > 0 && (
        <section aria-label="Daftar Dokumen Korpus" className="space-y-4">
          <p className="text-xs font-medium text-slate-600">
            Menampilkan {payload.items.length} dari {payload.total} dokumen
            terindeks
          </p>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {payload.items.map((doc) => {
              const safeUrl = getSafeExternalUrl(doc.source_url);
              return (
                <Card key={doc.id} as="article" className="flex flex-col justify-between space-y-4">
                  <div className="space-y-2.5">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-brand-700">
                        {doc.source_name}
                      </span>
                      <Badge variant={doc.is_synthetic_demo ? "warning" : "success"}>
                        {doc.is_synthetic_demo ? "Simulasi Demo" : "Terkurasi"}
                      </Badge>
                    </div>

                    <h3 className="text-base font-bold leading-snug text-slate-900">
                      {doc.title}
                    </h3>

                    {doc.authors && (
                      <p className="text-xs text-slate-600">
                        Penerbit / Penulis: {doc.authors}
                      </p>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3 text-xs text-slate-500">
                    <span>
                      {doc.chunks_count} potongan •{" "}
                      <code className="font-mono">{doc.source_type}</code>
                    </span>
                    <div className="flex flex-wrap items-center gap-3">
                      <Link
                        href={`/verify?claim=${encodeURIComponent(doc.title)}`}
                        className="font-semibold text-slate-700 hover:text-brand-600 hover:underline"
                      >
                        Uji Klaim Terkait
                      </Link>
                      {safeUrl ? (
                        <a
                          href={safeUrl}
                          target="_blank"
                          rel="noopener noreferrer nofollow"
                          className="font-semibold text-brand-600 hover:text-brand-700 hover:underline"
                        >
                          Buka Rujukan Asli &rarr;
                        </a>
                      ) : (
                        <span className="text-slate-400">Tautan tidak tersedia</span>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {payload.total > PAGE_SIZE && (
            <nav
              aria-label="Paginasi Dokumen Korpus"
              className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200/70 bg-white px-4 py-3 text-xs shadow-sm"
            >
              <span className="font-medium text-slate-600">
                Halaman {Math.floor(offset / PAGE_SIZE) + 1} dari{" "}
                {Math.max(1, Math.ceil(payload.total / PAGE_SIZE))}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={offset === 0}
                  onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
                  className="rounded-full border border-slate-200 bg-white px-4 py-1.5 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-45"
                >
                  Halaman Sebelumnya
                </button>
                <button
                  type="button"
                  disabled={offset + payload.items.length >= payload.total}
                  onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
                  className="rounded-full border border-slate-200 bg-white px-4 py-1.5 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-45"
                >
                  Halaman Selanjutnya
                </button>
              </div>
            </nav>
          )}
        </section>
      )}
    </div>
  );
}
