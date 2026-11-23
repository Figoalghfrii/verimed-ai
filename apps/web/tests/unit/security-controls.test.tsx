import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthCheckDataSchema } from "@/features/system-status/schemas/health-schema";
import { EvidenceStatsDataSchema } from "@/features/system-status/schemas/evidence-stats-schema";
import { EvidenceSourceCard } from "@/features/verification/components/evidence-source-card";
import {
  clearVerificationHistory,
  isHistoryExpired,
  loadVerificationHistory,
  saveVerificationToHistory,
} from "@/features/verification/lib/verification-history";
import { VerificationResponseData } from "@/features/verification/schemas/verification-schema";
import { parsePublicEnv } from "@/lib/env";
import { getSafeExternalUrl } from "@/lib/safe-url";

describe("Frontend Security Controls (VM-05, VM-07, VM-08, VM-28)", () => {
  it("blocks javascript:, data:, http:, and userinfo URLs while allowing clean https:// (VM-07)", () => {
    expect(getSafeExternalUrl("javascript:alert(1)")).toBeNull();
    expect(getSafeExternalUrl("data:text/html,<script>alert(1)</script>")).toBeNull();
    expect(getSafeExternalUrl("http://kemkes.go.id/artikel")).toBeNull();
    expect(getSafeExternalUrl("https://user:pass@kemkes.go.id/artikel")).toBeNull();
    expect(getSafeExternalUrl("https://kemkes.go.id/id/ctps")).toBe(
      "https://kemkes.go.id/id/ctps"
    );
  });

  it("renders javascript: source_url safely without creating a clickable anchor (VM-07)", () => {
    render(
      <EvidenceSourceCard
        source={{
          chunk_id: "c-xss",
          citation_key: "[1]",
          source_name: "Untrusted Source",
          source_type: "OFFICIAL_GUIDELINE",
          title: "XSS Guard Check",
          source_url: "javascript:alert(document.domain)",
          publication_date: null,
          excerpt: "Kutipan bukti uji keamanan.",
          stance: "CONTEXTUAL",
          relevance_score: 0.88,
          is_synthetic_demo: false,
        }}
      />
    );

    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(
      screen.getByText("javascript:alert(document.domain)")
    ).toBeInTheDocument();
  });

  it("redacts claim text in localStorage by default and auto-prunes expired TTL entries (VM-08)", () => {
    clearVerificationHistory();
    const sample: VerificationResponseData = {
      request_id: "77777777-7777-7777-7777-777777777777",
      status: "COMPLETED",
      language: "id",
      is_demonstration: false,
      persisted: true,
      emergency_triggered: false,
      emergency_guidance: null,
      processing_time_ms: 10,
      model_version: "mock-0.1.0",
      disclaimer: "Bukan alat diagnosis medis.",
      feedback_token: "token-123",
      claims: [
        {
          claim_index: 1,
          assessment_id: null,
          claim_text: "Klaim kesehatan sensitif pengguna.",
          normalized_query: "sensitif pengguna",
          verdict: "SUPPORTED",
          verdict_label_id: "Didukung Bukti",
          confidence_score: 0.9,
          abstained: false,
          abstention_reason: null,
          explanation: "Penjelasan bukti [1].",
          uncertainty_notes: "Catatan.",
          citations_valid: true,
          sources: [],
        },
      ],
    };

    saveVerificationToHistory(sample);
    const loadedDefault = loadVerificationHistory();
    expect(loadedDefault).toHaveLength(1);
    expect(loadedDefault[0]?.result.claims[0]?.claim_text).not.toContain(
      "Klaim kesehatan sensitif"
    );

    // Explicitly expired record should be filtered out on load
    window.localStorage.setItem(
      "verimed_verification_history_v1",
      JSON.stringify([
        {
          saved_at: "2020-01-01T00:00:00.000Z",
          expires_at: "2020-01-02T00:00:00.000Z",
          result: sample,
        },
      ])
    );
    expect(
      isHistoryExpired({
        saved_at: "2020-01-01T00:00:00.000Z",
        expires_at: "2020-01-02T00:00:00.000Z",
      })
    ).toBe(true);
    expect(loadVerificationHistory()).toEqual([]);
  });

  it("enforces HTTPS API URL in non-local production builds (VM-28)", () => {
    expect(() =>
      parsePublicEnv({
        NEXT_PUBLIC_API_BASE_URL: "http://api.verimed.example.com/api/v1",
        NODE_ENV: "production",
      })
    ).toThrow(/https:\/\//);

    expect(
      parsePublicEnv({
        NEXT_PUBLIC_API_BASE_URL: "https://api.verimed.example.com/api/v1",
        NODE_ENV: "production",
      }).NEXT_PUBLIC_API_BASE_URL
    ).toBe("https://api.verimed.example.com/api/v1");
  });

  it("accepts redacted nullable metadata in production health & stats schemas (VM-05)", () => {
    const parsedHealth = HealthCheckDataSchema.parse({
      status: "healthy",
      service: "VeriMed API",
      version: null,
      environment: null,
      ai_provider: null,
      database: { status: "connected", pgvector_enabled: true, latency_ms: null },
      disclaimer: "Edukasi saja.",
    });
    expect(parsedHealth.version).toBeNull();

    const parsedStats = EvidenceStatsDataSchema.parse({
      documents_count: 10,
      chunks_count: 20,
      synthetic_documents_count: 0,
      ai_provider: null,
      embedding_backend: null,
      reranker_backend: null,
    });
    expect(parsedStats.ai_provider).toBeNull();
  });
});
