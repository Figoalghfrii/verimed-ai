import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import {
  FeedbackStatsApiResponse,
  FeedbackStatsApiResponseSchema,
} from "../schemas/feedback-schema";

export async function fetchFeedbackStats(): Promise<FeedbackStatsApiResponse> {
  const raw = await apiFetch<unknown>("/feedback/stats");
  return FeedbackStatsApiResponseSchema.parse(raw);
}

export function useFeedbackStats() {
  return useQuery({
    queryKey: ["feedback-stats"],
    queryFn: fetchFeedbackStats,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
