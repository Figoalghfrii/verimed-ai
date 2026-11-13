import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClaimInputForm } from "@/features/verification/components/claim-input-form";
import { VerificationResultView } from "@/features/verification/components/verification-result-view";
import { VerificationResponseData } from "@/features/verification/schemas/verification-schema";

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

    render(<VerificationResultView result={mockResult} />);

    expect(
      screen.getByText(/Pemberitahuan Mode Demonstrasi/i)
    ).toBeInTheDocument();
    expect(screen.getByText("Didukung Bukti")).toBeInTheDocument();
    expect(
      screen.getByText("[Contoh Simulasi] Efektivitas Cuci Tangan")
    ).toBeInTheDocument();
    expect(screen.getByText(/bukan alat diagnosis medis/i)).toBeInTheDocument();
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

    render(<VerificationResultView result={emergencyResult} />);

    expect(
      screen.getByText("Terdeteksi Potensi Kondisi Darurat Medis")
    ).toBeInTheDocument();
    expect(screen.getByText(/119/)).toBeInTheDocument();
  });
});
