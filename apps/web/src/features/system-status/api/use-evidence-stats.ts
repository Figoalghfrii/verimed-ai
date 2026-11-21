import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import {
  EvidenceStatsResponse,
  EvidenceStatsResponseSchema,
} from "../schemas/evidence-stats-schema";

export async function fetchEvidenceStats(): Promise<EvidenceStatsResponse> {
  const raw = await apiFetch<unknown>("/evidence/stats");
  return EvidenceStatsResponseSchema.parse(raw);
}

export function useEvidenceStats() {
  return useQuery({
    queryKey: ["evidence-stats"],
    queryFn: fetchEvidenceStats,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
