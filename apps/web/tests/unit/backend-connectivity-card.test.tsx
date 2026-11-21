import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import { BackendConnectivityCard } from "@/features/system-status/components/backend-connectivity-card";

vi.mock("@/features/system-status/api/use-backend-health", () => ({
  useBackendHealth: () => ({
    isLoading: false,
    isError: false,
    isFetching: false,
    error: null,
    refetch: vi.fn(),
    data: {
      success: true,
      data: {
        status: "healthy",
        service: "VeriMed API",
        version: "0.1.0",
        environment: "test",
        ai_provider: "mock",
        database: {
          status: "connected",
          pgvector_enabled: true,
          latency_ms: 1.5,
        },
        disclaimer:
          "VeriMed adalah platform edukasi verifikasi klaim kesehatan berbasis bukti ilmiah, bukan alat diagnosis medis.",
      },
      meta: {
        request_id: "00000000-0000-0000-0000-000000000000",
        timestamp: "2026-10-31T05:00:00Z",
        api_version: "v1",
        is_demonstration: true,
      },
    },
  }),
}));

vi.mock("@/features/system-status/api/use-evidence-stats", () => ({
  useEvidenceStats: () => ({
    isLoading: false,
    isFetching: false,
    refetch: vi.fn(),
    data: {
      success: true,
      data: {
        documents_count: 12,
        chunks_count: 28,
        synthetic_documents_count: 5,
        ai_provider: "mock",
        embedding_backend: "hash",
        reranker_backend: "lexical",
      },
      meta: {
        request_id: "00000000-0000-0000-0000-000000000001",
        timestamp: "2026-10-31T05:00:00Z",
        api_version: "v1",
        is_demonstration: true,
      },
    },
  }),
}));

describe("BackendConnectivityCard", () => {
  it("renders backend API, PostgreSQL pgvector health, and evidence corpus stats", async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <BackendConnectivityCard />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Aktif (Healthy)")).toBeInTheDocument();
    });

    expect(screen.getByText("Terhubung")).toBeInTheDocument();
    expect(screen.getByText(/MOCK \(Mode Demonstrasi\)/i)).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("28")).toBeInTheDocument();
    expect(screen.getByText(/7 terkurasi • 5 simulasi/i)).toBeInTheDocument();
    expect(
      screen.getByText(/bukan alat diagnosis medis/i)
    ).toBeInTheDocument();
  });
});
