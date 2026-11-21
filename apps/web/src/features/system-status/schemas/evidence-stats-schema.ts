import { z } from "zod";
import { ResponseMetaSchema } from "./health-schema";

export const EvidenceStatsDataSchema = z.object({
  documents_count: z.number().int().nonnegative(),
  chunks_count: z.number().int().nonnegative(),
  synthetic_documents_count: z.number().int().nonnegative(),
  ai_provider: z.string(),
  embedding_backend: z.string(),
  reranker_backend: z.string(),
});

export const EvidenceStatsResponseSchema = z.object({
  success: z.literal(true),
  data: EvidenceStatsDataSchema,
  meta: ResponseMetaSchema,
});

export type EvidenceStatsData = z.infer<typeof EvidenceStatsDataSchema>;
export type EvidenceStatsResponse = z.infer<typeof EvidenceStatsResponseSchema>;
