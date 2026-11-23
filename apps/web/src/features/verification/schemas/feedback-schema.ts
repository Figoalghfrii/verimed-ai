import { z } from "zod";
import { ResponseMetaSchema } from "@/features/system-status/schemas/health-schema";

export const FeedbackCategoryEnum = z.enum([
  "CLARITY",
  "CITATIONS",
  "ACCURACY_CONCERN",
  "OTHER",
]);

export type FeedbackCategory = z.infer<typeof FeedbackCategoryEnum>;

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const FeedbackInputSchema = z.object({
  request_id: z.string().regex(UUID_PATTERN, "ID permintaan tidak valid."),
  assessment_id: z
    .string()
    .regex(UUID_PATTERN, "ID penilaian tidak valid.")
    .nullable()
    .optional(),
  is_helpful: z.boolean(),
  feedback_category: FeedbackCategoryEnum.nullable().optional(),
  comment: z
    .string()
    .trim()
    .max(500, "Komentar masukan maksimal 500 karakter.")
    .nullable()
    .optional(),
  feedback_token: z.string().max(1024).nullable().optional(),
});

export type FeedbackInput = z.infer<typeof FeedbackInputSchema>;

export const FeedbackResponseDataSchema = z.object({
  feedback_id: z.string(),
  request_id: z.string(),
  is_helpful: z.boolean(),
  feedback_category: FeedbackCategoryEnum.nullable(),
  persisted: z.boolean(),
  message: z.string(),
});

export type FeedbackResponseData = z.infer<typeof FeedbackResponseDataSchema>;

export const FeedbackApiResponseSchema = z.object({
  success: z.literal(true),
  data: FeedbackResponseDataSchema,
  meta: ResponseMetaSchema,
});

export type FeedbackApiResponse = z.infer<typeof FeedbackApiResponseSchema>;

export const FeedbackStatsDataSchema = z.object({
  total_count: z.number().int().nonnegative(),
  helpful_count: z.number().int().nonnegative(),
  not_helpful_count: z.number().int().nonnegative(),
  helpful_rate: z.number().min(0).max(1),
  by_category: z.record(z.string(), z.number().int().nonnegative()),
  database_connected: z.boolean(),
});

export const FeedbackStatsApiResponseSchema = z.object({
  success: z.literal(true),
  data: FeedbackStatsDataSchema,
  meta: ResponseMetaSchema,
});

export type FeedbackStatsData = z.infer<typeof FeedbackStatsDataSchema>;
export type FeedbackStatsApiResponse = z.infer<
  typeof FeedbackStatsApiResponseSchema
>;
