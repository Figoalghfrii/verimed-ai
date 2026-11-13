import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TopNavbar } from "@/components/layout/top-navbar";
import { EvidenceHeroShowcase } from "@/features/system-status/components/evidence-hero-showcase";

vi.mock("next/navigation", () => ({
  usePathname: () => "/verify",
}));

describe("Redesigned VeriMed UI", () => {
  it("highlights active navigation pill in TopNavbar", () => {
    render(<TopNavbar />);

    const verifyLink = screen.getByRole("link", { name: "Verifikasi Klaim" });
    expect(verifyLink).toHaveAttribute("aria-current", "page");
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
});
