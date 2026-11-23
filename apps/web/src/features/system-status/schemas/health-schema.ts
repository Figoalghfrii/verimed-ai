import { z } from "zod";

export const ResponseMetaSchema = z.object({
  request_id: z.string(),
  timestamp: z.string(),
  api_version: z.string(),
  is_demonstration: z.boolean(),
});

export const DatabaseHealthStatusSchema = z.object({
  status: z.enum(["connected", "degraded", "disconnected"]),
  pgvector_enabled: z.boolean(),
  latency_ms: z.number().nullable(),
});

export const HealthCheckDataSchema = z.object({
  status: z.enum(["healthy", "degraded"]),
  service: z.string(),
  version: z.string().nullable().optional().default(null),
  environment: z.string().nullable().optional().default(null),
  ai_provider: z.string().nullable().optional().default(null),
  database: DatabaseHealthStatusSchema,
  disclaimer: z.string(),
});

export const HealthCheckResponseSchema = z.object({
  success: z.literal(true),
  data: HealthCheckDataSchema,
  meta: ResponseMetaSchema,
});

export type HealthCheckResponse = z.infer<typeof HealthCheckResponseSchema>;
export type HealthCheckData = z.infer<typeof HealthCheckDataSchema>;
