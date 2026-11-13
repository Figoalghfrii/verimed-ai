import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import {
  VerificationApiResponse,
  VerificationApiResponseSchema,
  VerifyClaimInput,
} from "../schemas/verification-schema";

export async function submitClaimVerification(
  input: VerifyClaimInput
): Promise<VerificationApiResponse> {
  const raw = await apiFetch<unknown>("/verify", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return VerificationApiResponseSchema.parse(raw);
}

export function useVerifyClaim() {
  return useMutation({
    mutationFn: submitClaimVerification,
  });
}
