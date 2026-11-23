import { z } from "zod";
import { ResponseMetaSchema } from "@/features/system-status/schemas/health-schema";

export const VerdictEnum = z.enum([
  "SUPPORTED",
  "CONTRADICTED",
  "MIXED_EVIDENCE",
  "INSUFFICIENT_EVIDENCE",
]);

export type VerdictLabel = z.infer<typeof VerdictEnum>;

export const CitationStanceEnum = z.enum([
  "SUPPORTING",
  "CONTRADICTING",
  "CONTEXTUAL",
]);

export const VerifyClaimInputSchema = z.object({
  text: z
    .string()
    .trim()
    .min(10, "Klaim kesehatan minimal terdiri dari 10 karakter.")
    .max(1000, "Klaim kesehatan maksimal 1.000 karakter."),
  language: z.enum(["id", "en"]).default("id"),
});

export type VerifyClaimInput = z.infer<typeof VerifyClaimInputSchema>;

export const EvidenceSourceItemSchema = z.object({
  chunk_id: z.string(),
  citation_key: z.string(),
  source_name: z.string(),
  source_type: z.string(),
  title: z.string(),
  source_url: z.string(),
  publication_date: z.string().nullable(),
  excerpt: z.string(),
  stance: CitationStanceEnum,
  relevance_score: z.number(),
  is_synthetic_demo: z.boolean(),
});

export type EvidenceSourceItem = z.infer<typeof EvidenceSourceItemSchema>;

export const EmergencyGuidanceSchema = z.object({
  headline: z.string(),
  message: z.string(),
  emergency_contacts: z.array(z.string()),
});

export type EmergencyGuidance = z.infer<typeof EmergencyGuidanceSchema>;

export const ClaimVerificationResultSchema = z.object({
  claim_index: z.number(),
  assessment_id: z.string().nullable().optional(),
  claim_text: z.string(),
  normalized_query: z.string(),
  verdict: VerdictEnum,
  verdict_label_id: z.string(),
  confidence_score: z.number(),
  abstained: z.boolean(),
  abstention_reason: z.string().nullable(),
  explanation: z.string(),
  uncertainty_notes: z.string(),
  citations_valid: z.boolean(),
  sources: z.array(EvidenceSourceItemSchema),
});

export type ClaimVerificationResult = z.infer<
  typeof ClaimVerificationResultSchema
>;

export const VerificationResponseDataSchema = z.object({
  request_id: z.string(),
  status: z.enum(["COMPLETED", "EMERGENCY_HALT"]),
  language: z.enum(["id", "en"]),
  is_demonstration: z.boolean(),
  persisted: z.boolean(),
  emergency_triggered: z.boolean(),
  emergency_guidance: EmergencyGuidanceSchema.nullable(),
  claims: z.array(ClaimVerificationResultSchema),
  processing_time_ms: z.number(),
  model_version: z.string(),
  disclaimer: z.string(),
  feedback_token: z.string().nullable().optional(),
});

export type VerificationResponseData = z.infer<
  typeof VerificationResponseDataSchema
>;

export const VerificationApiResponseSchema = z.object({
  success: z.literal(true),
  data: VerificationResponseDataSchema,
  meta: ResponseMetaSchema,
});

export type VerificationApiResponse = z.infer<
  typeof VerificationApiResponseSchema
>;
