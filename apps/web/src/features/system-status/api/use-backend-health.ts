import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import {
  HealthCheckResponse,
  HealthCheckResponseSchema,
} from "../schemas/health-schema";

export async function fetchBackendHealth(): Promise<HealthCheckResponse> {
  const raw = await apiFetch<unknown>("/health");
  return HealthCheckResponseSchema.parse(raw);
}

export function useBackendHealth() {
  return useQuery({
    queryKey: ["system-health"],
    queryFn: fetchBackendHealth,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
