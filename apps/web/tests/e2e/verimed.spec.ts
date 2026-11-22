import { expect, test } from "@playwright/test";

const META = {
  request_id: "11111111-1111-1111-1111-111111111111",
  timestamp: "2026-11-21T17:00:00Z",
  api_version: "v1",
  is_demonstration: true,
};

test.describe("VeriMed End-to-End Flows", () => {
  test("home page renders hero, medical disclaimer, and live backend health status", async ({
    page,
  }) => {
    await page.route("**/api/v1/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
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
              "VeriMed adalah platform edukasi verifikasi klaim kesehatan, bukan alat diagnosis medis.",
          },
          meta: META,
        }),
      });
    });

    await page.route("**/api/v1/evidence/stats", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            documents_count: 8,
            chunks_count: 16,
            synthetic_documents_count: 5,
            ai_provider: "mock",
            embedding_backend: "hash",
            reranker_backend: "lexical",
          },
          meta: META,
        }),
      });
    });

    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /Verifikasi Klaim Kesehatan/i })
    ).toBeVisible();
    await expect(page.getByText(/VeriMed API/i)).toBeVisible();
    await expect(page.getByText(/3 terkurasi • 5 simulasi/i)).toBeVisible();
    await expect(page.getByText(/bukan alat diagnosis medis/i).first()).toBeVisible();
  });

  test("verify page evaluates claim, displays grounded result, and submits user feedback", async ({
    page,
  }) => {
    await page.route("**/api/v1/verify", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            request_id: "22222222-2222-2222-2222-222222222222",
            status: "COMPLETED",
            language: "id",
            is_demonstration: true,
            persisted: true,
            emergency_triggered: false,
            emergency_guidance: null,
            claims: [
              {
                claim_index: 1,
                claim_text:
                  "Mencuci tangan pakai sabun membantu mencegah penularan infeksi.",
                normalized_query: "cuci tangan sabun infeksi",
                verdict: "SUPPORTED",
                verdict_label_id: "Didukung Bukti",
                confidence_score: 0.92,
                abstained: false,
                abstention_reason: null,
                explanation:
                  "Berdasarkan bukti terkurasi, cuci tangan pakai sabun efektif menurunkan risiko infeksi [1].",
                uncertainty_notes:
                  "Penilaian berdasarkan korpus bukti terindeks VeriMed.",
                citations_valid: true,
                sources: [
                  {
                    chunk_id: "chunk-ctps-1",
                    citation_key: "[1]",
                    source_name: "VeriMed Demo Corpus",
                    source_type: "SYNTHETIC_DEMO_GUIDELINE",
                    title: "[Contoh Simulasi] Efektivitas Cuci Tangan Pakai Sabun",
                    source_url: "https://demo.verimed.local/synthetic/ctps-infeksi",
                    publication_date: "2025-01-15",
                    excerpt:
                      "Kebiasaan mencuci tangan dengan sabun menurunkan risiko infeksi saluran pencernaan.",
                    stance: "SUPPORTING",
                    relevance_score: 0.92,
                    is_synthetic_demo: true,
                  },
                ],
              },
            ],
            processing_time_ms: 15,
            model_version: "mock-0.1.0",
            disclaimer:
              "VeriMed adalah platform edukasi verifikasi klaim kesehatan, bukan alat diagnosis medis.",
          },
          meta: META,
        }),
      });
    });

    await page.route("**/api/v1/feedback", async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            feedback_id: "33333333-3333-3333-3333-333333333333",
            request_id: "22222222-2222-2222-2222-222222222222",
            is_helpful: true,
            feedback_category: "CLARITY",
            persisted: true,
            message:
              "Terima kasih! Masukan Anda membantu meningkatkan kejelasan penjelasan VeriMed.",
          },
          meta: { ...META, is_demonstration: false },
        }),
      });
    });

    await page.goto("/verify");
    await page
      .getByLabel("Teks Klaim Kesehatan")
      .fill("Mencuci tangan pakai sabun membantu mencegah penularan infeksi.");
    await page.getByRole("button", { name: "Periksa Klaim" }).click();

    await expect(
      page
        .getByRole("region", { name: "Hasil Pemeriksaan Bukti" })
        .getByText("Didukung Bukti")
    ).toBeVisible();
    await expect(
      page.getByText("[Contoh Simulasi] Efektivitas Cuci Tangan Pakai Sabun")
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Salin Ringkasan Bukti" })
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Riwayat Pemeriksaan Lokal" })
    ).toBeVisible();

    await page.getByRole("button", { name: "Ya, Membantu" }).click();
    await page
      .getByLabel(/Catatan Tambahan/i)
      .fill("Penjelasan mudah dipahami.");
    await page.getByRole("button", { name: "Kirim Masukan" }).click();

    await expect(
      page.getByText(/Terima kasih! Masukan Anda membantu meningkatkan/i)
    ).toBeVisible();
  });

  test("verify page halts on acute medical emergency and displays 119 guidance", async ({
    page,
  }) => {
    await page.route("**/api/v1/verify", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            request_id: "44444444-4444-4444-4444-444444444444",
            status: "EMERGENCY_HALT",
            language: "id",
            is_demonstration: true,
            persisted: false,
            emergency_triggered: true,
            emergency_guidance: {
              headline: "Terdeteksi Potensi Kondisi Darurat Medis",
              message:
                "Segera hubungi layanan darurat medis atau kunjungi IGD terdekat.",
              emergency_contacts: [
                "Ambulans / Kementerian Kesehatan RI: 119",
                "Instalasi Gawat Darurat (IGD) Rumah Sakit Terdekat",
              ],
            },
            claims: [],
            processing_time_ms: 5,
            model_version: "mock-0.1.0",
            disclaimer:
              "VeriMed adalah platform edukasi verifikasi klaim kesehatan, bukan alat diagnosis medis.",
          },
          meta: META,
        }),
      });
    });

    await page.goto("/verify");
    await page
      .getByLabel("Teks Klaim Kesehatan")
      .fill("Saya mengalami nyeri dada hebat dan sesak napas mendadak.");
    await page.getByRole("button", { name: "Periksa Klaim" }).click();

    await expect(
      page.getByText("Terdeteksi Potensi Kondisi Darurat Medis")
    ).toBeVisible();
    await expect(
      page.getByText("Ambulans / Kementerian Kesehatan RI: 119")
    ).toBeVisible();
  });

  test("about page explains methodology pipeline, safety limits, and feedback stats", async ({
    page,
  }) => {
    await page.route("**/api/v1/feedback/stats", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            total_count: 10,
            helpful_count: 9,
            not_helpful_count: 1,
            helpful_rate: 0.9,
            by_category: { CLARITY: 8, CITATIONS: 2 },
            database_connected: true,
          },
          meta: META,
        }),
      });
    });

    await page.goto("/about");
    await expect(
      page.getByRole("heading", {
        name: /Tentang VeriMed & Metodologi Verifikasi/i,
      })
    ).toBeVisible();
    await expect(
      page.getByText(/Validasi Input & Gerbang Darurat Medis/i)
    ).toBeVisible();
    await expect(page.getByText("90%")).toBeVisible();
  });

  test("corpus page lists indexed curated sources and supports filtering", async ({
    page,
  }) => {
    await page.route("**/api/v1/evidence/documents*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            items: [
              {
                id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                source_name: "Kementerian Kesehatan RI",
                source_url:
                  "https://kemkes.go.id/id/cuci-tangan-pakai-sabun-perilaku-sederhana-berdampak-luar-biasa",
                title:
                  "Cuci Tangan Pakai Sabun, Perilaku Sederhana Berdampak Luar Biasa",
                authors: "Kementerian Kesehatan Republik Indonesia",
                publication_date: null,
                language_code: "id",
                source_type: "OFFICIAL_GUIDELINE",
                chunks_count: 2,
                is_synthetic_demo: false,
                retrieved_at: "2026-11-22T05:00:00Z",
              },
            ],
            total: 1,
            limit: 20,
            offset: 0,
            database_connected: true,
          },
          meta: { ...META, is_demonstration: false },
        }),
      });
    });

    await page.goto("/corpus");
    await expect(
      page.getByRole("heading", { name: /Direktori Korpus Bukti Publik/i })
    ).toBeVisible();
    await expect(
      page.getByText(
        "Cuci Tangan Pakai Sabun, Perilaku Sederhana Berdampak Luar Biasa"
      )
    ).toBeVisible();
    await expect(page.getByText("Terkurasi", { exact: true })).toBeVisible();
  });
});
