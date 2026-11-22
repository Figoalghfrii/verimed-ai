import { z } from "zod";
import { ResponseMetaSchema } from "@/features/system-status/schemas/health-schema";

export const EvidenceDocumentItemSchema = z.object({
  id: z.string(),
  source_name: z.string(),
  source_url: z.string(),
  title: z.string(),
  authors: z.string().nullable(),
  publication_date: z.string().nullable(),
  language_code: z.string(),
  source_type: z.string(),
  chunks_count: z.number().int().nonnegative(),
  is_synthetic_demo: z.boolean(),
  retrieved_at: z.string(),
});

export type EvidenceDocumentItem = z.infer<typeof EvidenceDocumentItemSchema>;

export const EvidenceDocumentListDataSchema = z.object({
  items: z.array(EvidenceDocumentItemSchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
  offset: z.number().int().nonnegative(),
  database_connected: z.boolean(),
});

export type EvidenceDocumentListData = z.infer<
  typeof EvidenceDocumentListDataSchema
>;

export const EvidenceDocumentListResponseSchema = z.object({
  success: z.literal(true),
  data: EvidenceDocumentListDataSchema,
  meta: ResponseMetaSchema,
});

export type EvidenceDocumentListResponse = z.infer<
  typeof EvidenceDocumentListResponseSchema
>;
