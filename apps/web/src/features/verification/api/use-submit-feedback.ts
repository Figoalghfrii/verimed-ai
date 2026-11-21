import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import {
  FeedbackApiResponse,
  FeedbackApiResponseSchema,
  FeedbackInput,
} from "../schemas/feedback-schema";

export async function submitVerificationFeedback(
  input: FeedbackInput
): Promise<FeedbackApiResponse> {
  const raw = await apiFetch<unknown>("/feedback", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return FeedbackApiResponseSchema.parse(raw);
}

export function useSubmitFeedback() {
  return useMutation({
    mutationFn: submitVerificationFeedback,
  });
}
