import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import { TopNavbar } from "@/components/layout/top-navbar";
import { CorpusExplorer } from "@/features/corpus/components/corpus-explorer";
import { EvidenceHeroShowcase } from "@/features/system-status/components/evidence-hero-showcase";

vi.mock("next/navigation", () => ({
  usePathname: () => "/verify",
}));

vi.mock("@/features/corpus/api/use-evidence-documents", () => ({
  useEvidenceDocuments: (params: { q?: string; sourceType?: string }) => ({
    isLoading: false,
    isError: false,
    error: null,
    data: {
      success: true,
      data: {
        items: [
          {
            id: "doc-1",
            source_name: "Kementerian Kesehatan RI",
            source_url: "https://kemkes.go.id/id/ctps",
            title: "Cuci Tangan Pakai Sabun",
            authors: "Kemenkes RI",
            publication_date: null,
            language_code: "id",
            source_type: "OFFICIAL_GUIDELINE",
            chunks_count: 2,
            is_synthetic_demo: false,
            retrieved_at: "2026-11-22T05:00:00Z",
          },
        ].filter((item) =>
          params.q
            ? item.title.toLowerCase().includes(params.q.toLowerCase())
            : true
        ),
        total: 1,
        limit: 20,
        offset: 0,
        database_connected: true,
      },
      meta: {
        request_id: "00000000-0000-0000-0000-000000000002",
        timestamp: "2026-11-22T05:00:00Z",
        api_version: "v1",
        is_demonstration: false,
      },
    },
  }),
}));

describe("Redesigned VeriMed UI", () => {
  it("highlights active navigation pill in TopNavbar including Korpus Bukti", () => {
    render(<TopNavbar />);

    const verifyLink = screen.getByRole("link", { name: "Verifikasi Klaim" });
    expect(verifyLink).toHaveAttribute("aria-current", "page");
    expect(
      screen.getByRole("link", { name: "Korpus Bukti" })
    ).toHaveAttribute("href", "/corpus");
    expect(
      screen.getByRole("link", { name: "Ringkasan" })
    ).not.toHaveAttribute("aria-current");
  });

  it("renders EvidenceHeroShowcase with calibrated verdict labels and bento cards", () => {
    render(<EvidenceHeroShowcase />);

    expect(
      screen.getByText("Verifikasi Klaim Kesehatan Berbasis Bukti Ilmiah")
    ).toBeInTheDocument();
    expect(screen.getByText("Didukung Bukti")).toBeInTheDocument();
    expect(screen.getByText("Bukti Tidak Cukup")).toBeInTheDocument();
    expect(screen.getByText("Integritas Bukti")).toBeInTheDocument();
    expect(screen.getByText("Ambang Abstain")).toBeInTheDocument();
    expect(screen.getByText("Validasi Sitasi")).toBeInTheDocument();
  });

  it("renders CorpusExplorer with curated source badge and search filter", () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <CorpusExplorer />
      </QueryClientProvider>
    );

    expect(screen.getByText("Cuci Tangan Pakai Sabun")).toBeInTheDocument();
    expect(screen.getByText("Terkurasi")).toBeInTheDocument();

    const searchInput = screen.getByLabelText(
      "Cari judul atau penerbit dokumen bukti"
    );
    fireEvent.change(searchInput, { target: { value: "tidak-ada" } });
    fireEvent.click(screen.getByRole("button", { name: "Cari Sumber" }));

    expect(
      screen.getByText(/Tidak ada dokumen bukti yang cocok/i)
    ).toBeInTheDocument();
  });
});
