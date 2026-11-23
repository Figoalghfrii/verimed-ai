import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClaimInputForm } from "@/features/verification/components/claim-input-form";
import { FeedbackWidget } from "@/features/verification/components/feedback-widget";
import { VerificationResultView } from "@/features/verification/components/verification-result-view";
import {
  clearVerificationHistory,
  formatWhatsAppSummary,
  loadVerificationHistory,
  saveVerificationToHistory,
} from "@/features/verification/lib/verification-history";
import { VerificationResponseData } from "@/features/verification/schemas/verification-schema";

function renderWithQueryClient(ui: React.ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>{ui}</QueryClientProvider>
  );
}

describe("ClaimInputForm", () => {
  it("shows validation error for claims shorter than 10 characters", () => {
    const onSubmit = vi.fn();
    render(<ClaimInputForm onSubmit={onSubmit} isSubmitting={false} />);

    const textarea = screen.getByLabelText("Teks Klaim Kesehatan");
    fireEvent.change(textarea, { target: { value: "pendek" } });
    fireEvent.click(screen.getByRole("button", { name: "Periksa Klaim" }));

    expect(
      screen.getByText(/minimal terdiri dari 10 karakter/i)
    ).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits valid claim text", () => {
    const onSubmit = vi.fn();
    render(<ClaimInputForm onSubmit={onSubmit} isSubmitting={false} />);

    const textarea = screen.getByLabelText("Teks Klaim Kesehatan");
    fireEvent.change(textarea, {
      target: {
        value:
          "Mencuci tangan pakai sabun membantu mencegah penularan infeksi.",
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Periksa Klaim" }));

    expect(onSubmit).toHaveBeenCalledWith({
      text: "Mencuci tangan pakai sabun membantu mencegah penularan infeksi.",
      language: "id",
    });
  });

  it("supports switching claim language to English and shows English sample chips", () => {
    const onSubmit = vi.fn();
    render(<ClaimInputForm onSubmit={onSubmit} isSubmitting={false} />);

    fireEvent.change(screen.getByLabelText("Bahasa Klaim:"), {
      target: { value: "en" },
    });
    expect(
      screen.getByRole("button", { name: "Handwashing & Infection" })
    ).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Teks Klaim Kesehatan"), {
      target: { value: "Washing hands with soap reduces infection risk." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Periksa Klaim" }));

    expect(onSubmit).toHaveBeenCalledWith({
      text: "Washing hands with soap reduces infection risk.",
      language: "en",
    });
  });
});

describe("VerificationResultView", () => {
  it("renders demonstration banner, verdict badge, source card, and disclaimer", () => {
    const mockResult: VerificationResponseData = {
      request_id: "11111111-1111-1111-1111-111111111111",
      status: "COMPLETED",
      language: "id",
      is_demonstration: true,
      persisted: false,
      emergency_triggered: false,
      emergency_guidance: null,
      processing_time_ms: 12,
      model_version: "mock-0.1.0",
      disclaimer:
        "VeriMed adalah platform edukasi verifikasi klaim kesehatan, bukan alat diagnosis medis.",
      claims: [
        {
          claim_index: 1,
          claim_text: "Cuci tangan pakai sabun mencegah infeksi.",
          normalized_query: "cuci tangan pakai sabun mencegah infeksi",
          verdict: "SUPPORTED",
          verdict_label_id: "Didukung Bukti",
          confidence_score: 0.92,
          abstained: false,
          abstention_reason: null,
          explanation: "Klaim sesuai dengan ringkasan bukti demonstrasi [1].",
          uncertainty_notes: "Menggunakan data simulasi demonstrasi.",
          citations_valid: true,
          sources: [
            {
              chunk_id: "demo-ctps-001",
              citation_key: "[1]",
              source_name: "VeriMed Demo Corpus",
              source_type: "SYNTHETIC_DEMO_GUIDELINE",
              title: "[Contoh Simulasi] Efektivitas Cuci Tangan",
              source_url: "https://demo.verimed.local/synthetic/ctps-infeksi",
              publication_date: "2025-01-15",
              excerpt: "Data simulasi demonstrasi kebersihan tangan.",
              stance: "SUPPORTING",
              relevance_score: 0.92,
              is_synthetic_demo: true,
            },
          ],
        },
      ],
    };

    renderWithQueryClient(<VerificationResultView result={mockResult} />);

    expect(
      screen.getByText(/Pemberitahuan Mode Demonstrasi/i)
    ).toBeInTheDocument();
    expect(screen.getByText("Didukung Bukti")).toBeInTheDocument();
    expect(
      screen.getByText("[Contoh Simulasi] Efektivitas Cuci Tangan")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Cetak / Simpan PDF" })
    ).toBeInTheDocument();
    expect(screen.getByText(/bukan alat diagnosis medis/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Apakah penjelasan verifikasi ini mudah dipahami/i)
    ).toBeInTheDocument();
  });

  it("renders Indonesian emergency alert when emergency_triggered is true", () => {
    const emergencyResult: VerificationResponseData = {
      request_id: "22222222-2222-2222-2222-222222222222",
      status: "EMERGENCY_HALT",
      language: "id",
      is_demonstration: true,
      persisted: false,
      emergency_triggered: true,
      emergency_guidance: {
        headline: "Terdeteksi Potensi Kondisi Darurat Medis",
        message: "Segera cari pertolongan medis darurat.",
        emergency_contacts: ["Ambulans / Kementerian Kesehatan RI: 119"],
      },
      claims: [],
      processing_time_ms: 4,
      model_version: "mock-0.1.0",
      disclaimer: "Bukan alat diagnosis medis.",
    };

    renderWithQueryClient(<VerificationResultView result={emergencyResult} />);

    expect(
      screen.getByText("Terdeteksi Potensi Kondisi Darurat Medis")
    ).toBeInTheDocument();
    expect(screen.getByText(/119/)).toBeInTheDocument();
    expect(
      screen.queryByText(/Apakah penjelasan verifikasi ini mudah dipahami/i)
    ).not.toBeInTheDocument();
  });
});

describe("FeedbackWidget", () => {
  it("submits feedback via API when verification is persisted", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          success: true,
          data: {
            feedback_id: "33333333-3333-3333-3333-333333333333",
            request_id: "11111111-1111-1111-1111-111111111111",
            is_helpful: true,
            feedback_category: "CLARITY",
            persisted: true,
            message: "Terima kasih atas masukan Anda.",
          },
          meta: {
            request_id: "44444444-4444-4444-4444-444444444444",
            timestamp: "2026-11-21T17:00:00Z",
            api_version: "v1",
            is_demonstration: false,
          },
        }),
        { status: 201, headers: { "Content-Type": "application/json" } }
      )
    );

    renderWithQueryClient(
      <FeedbackWidget
        requestId="11111111-1111-1111-1111-111111111111"
        persisted={true}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Ya, Membantu" }));
    fireEvent.change(screen.getByLabelText(/Catatan Tambahan/i), {
      target: { value: "Penjelasan ringkas dan jelas." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Kirim Masukan" }));

    await waitFor(() => {
      expect(
        screen.getByText("Terima kasih atas masukan Anda.")
      ).toBeInTheDocument();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    fetchSpy.mockRestore();
  });

  it("acknowledges feedback locally in stateless demo mode without calling API", () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");

    renderWithQueryClient(
      <FeedbackWidget
        requestId="11111111-1111-1111-1111-111111111111"
        persisted={false}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Kurang Membantu" }));
    fireEvent.click(screen.getByRole("button", { name: "Kirim Masukan" }));

    expect(
      screen.getByText(/mode stateless tanpa basis data/i)
    ).toBeInTheDocument();
    expect(fetchSpy).not.toHaveBeenCalled();
    fetchSpy.mockRestore();
  });
});

describe("WhatsApp summary & local verification history", () => {
  const sampleResult: VerificationResponseData = {
    request_id: "55555555-5555-5555-5555-555555555555",
    status: "COMPLETED",
    language: "id",
    is_demonstration: false,
    persisted: true,
    emergency_triggered: false,
    emergency_guidance: null,
    processing_time_ms: 14,
    model_version: "hybrid-0.1.0",
    disclaimer: "Bukan alat diagnosis medis.",
    claims: [
      {
        claim_index: 1,
        claim_text: "Cuci tangan pakai sabun menurunkan risiko diare.",
        normalized_query: "cuci tangan sabun diare",
        verdict: "SUPPORTED",
        verdict_label_id: "Didukung Bukti",
        confidence_score: 0.91,
        abstained: false,
        abstention_reason: null,
        explanation: "CTPS efektif menurunkan risiko penularan diare [1].",
        uncertainty_notes: "Berdasarkan korpus terkurasi.",
        citations_valid: true,
        sources: [
          {
            chunk_id: "c1",
            citation_key: "[1]",
            source_name: "Kementerian Kesehatan RI",
            source_type: "OFFICIAL_GUIDELINE",
            title: "Cuci Tangan Pakai Sabun",
            source_url: "https://kemkes.go.id/id/ctps",
            publication_date: null,
            excerpt: "CTPS menurunkan risiko diare.",
            stance: "SUPPORTING",
            relevance_score: 0.91,
            is_synthetic_demo: false,
          },
        ],
      },
    ],
  };

  it("formats WhatsApp summary and copies it to clipboard on button click", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    const text = formatWhatsAppSummary(sampleResult);
    expect(text).toContain("*VeriMed — Ringkasan Pemeriksaan Bukti*");
    expect(text).toContain("Didukung Bukti (91% keyakinan)");
    expect(text).toContain("https://kemkes.go.id/id/ctps");

    renderWithQueryClient(<VerificationResultView result={sampleResult} />);
    fireEvent.click(
      screen.getByRole("button", { name: "Salin Ringkasan Bukti" })
    );

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Ringkasan Disalin!" })
      ).toBeInTheDocument();
    });
    expect(writeText).toHaveBeenCalledWith(text);
  });

  it("saves, loads, and clears local verification history safely", () => {
    clearVerificationHistory();
    expect(loadVerificationHistory()).toEqual([]);

    const saved = saveVerificationToHistory(sampleResult);
    expect(saved).toHaveLength(1);
    expect(loadVerificationHistory()[0]?.result.request_id).toBe(
      "55555555-5555-5555-5555-555555555555"
    );

    clearVerificationHistory();
    expect(loadVerificationHistory()).toEqual([]);
  });

  it("renders clickable external link for verified curated sources and prints report", () => {
    const printSpy = vi.spyOn(window, "print").mockImplementation(() => {});
    renderWithQueryClient(<VerificationResultView result={sampleResult} />);

    const externalLink = screen.getByRole("link", {
      name: "https://kemkes.go.id/id/ctps",
    });
    expect(externalLink).toHaveAttribute("target", "_blank");
    expect(externalLink).toHaveAttribute("rel", "noopener noreferrer nofollow");

    fireEvent.click(
      screen.getByRole("button", { name: "Cetak / Simpan PDF" })
    );
    expect(printSpy).toHaveBeenCalledTimes(1);
    printSpy.mockRestore();
  });
});
