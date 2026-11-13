import React from "react";
import { BackendConnectivityCard } from "@/features/system-status/components/backend-connectivity-card";
import { EvidenceHeroShowcase } from "@/features/system-status/components/evidence-hero-showcase";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <EvidenceHeroShowcase />
      <BackendConnectivityCard />
    </div>
  );
}
