import { z } from "zod";
import { ResponseMetaSchema } from "@/features/system-status/schemas/health-schema";

export const FeedbackCategoryEnum = z.enum([
  "CLARITY",
  "CITATIONS",
  "ACCURACY_CONCERN",
  "OTHER",
]);

export type FeedbackCategory = z.infer<typeof FeedbackCategoryEnum>;

export const FeedbackInputSchema = z.object({
  request_id: z.string().uuid(),
  is_helpful: z.boolean(),
  feedback_category: FeedbackCategoryEnum.nullable().optional(),
  comment: z
    .string()
    .trim()
    .max(500, "Komentar masukan maksimal 500 karakter.")
    .nullable()
    .optional(),
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
