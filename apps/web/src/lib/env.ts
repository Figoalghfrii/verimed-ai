import { z } from "zod";

const LOCAL_HOSTNAMES = new Set(["localhost", "127.0.0.1", "::1", "[::1]", "api"]);

export function parsePublicEnv(rawEnv?: {
  NEXT_PUBLIC_APP_NAME?: string;
  NEXT_PUBLIC_API_BASE_URL?: string;
  NODE_ENV?: string;
}) {
  const schema = z.object({
    NEXT_PUBLIC_APP_NAME: z.string().default("VeriMed"),
    NEXT_PUBLIC_API_BASE_URL: z
      .string()
      .url()
      .default("http://localhost:8000/api/v1"),
  });

  const parsed = schema.parse({
    NEXT_PUBLIC_APP_NAME:
      rawEnv?.NEXT_PUBLIC_APP_NAME ||
      process.env.NEXT_PUBLIC_APP_NAME ||
      "VeriMed",
    NEXT_PUBLIC_API_BASE_URL:
      rawEnv?.NEXT_PUBLIC_API_BASE_URL ||
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      "http://localhost:8000/api/v1",
  });

  const nodeEnv = rawEnv?.NODE_ENV ?? process.env.NODE_ENV;
  if (nodeEnv === "production") {
    const apiUrl = new URL(parsed.NEXT_PUBLIC_API_BASE_URL);
    if (!LOCAL_HOSTNAMES.has(apiUrl.hostname) && apiUrl.protocol !== "https:") {
      throw new Error(
        "NEXT_PUBLIC_API_BASE_URL must use https:// in non-local production builds."
      );
    }
  }

  return parsed;
}

export const publicEnv = parsePublicEnv();
