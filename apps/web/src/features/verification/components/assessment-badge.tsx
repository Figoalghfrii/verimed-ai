import React from "react";
import { Badge } from "@/components/ui/badge";
import { VerdictLabel } from "../schemas/verification-schema";

const VERDICT_CONFIG: Record<
  VerdictLabel,
  { label: string; variant: "success" | "danger" | "warning" | "neutral" }
> = {
  SUPPORTED: { label: "Didukung Bukti", variant: "success" },
  CONTRADICTED: { label: "Bertentangan dengan Bukti", variant: "danger" },
  MIXED_EVIDENCE: { label: "Bukti Beragam", variant: "warning" },
  INSUFFICIENT_EVIDENCE: { label: "Bukti Tidak Cukup", variant: "neutral" },
};

export function AssessmentBadge({ verdict }: { verdict: VerdictLabel }) {
  const config = VERDICT_CONFIG[verdict];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
