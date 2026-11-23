import { publicEnv } from "./env";

export class ApiClientError extends Error {
  public readonly statusCode: number;
  public readonly code: string;

  constructor(message: string, statusCode: number, code = "API_ERROR") {
    super(message);
    this.name = "ApiClientError";
    this.statusCode = statusCode;
    this.code = code;
  }
}

let cachedClientToken: string | null = null;

async function acquireAnonymousClientToken(baseUrl: string): Promise<string | null> {
  try {
    const tokenRes = await fetch(`${baseUrl}/client-token`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });
    if (!tokenRes.ok) {
      return null;
    }
    const tokenPayload = await tokenRes.json().catch(() => null);
    const token = tokenPayload?.data?.client_token;
    if (typeof token === "string" && token.length > 0) {
      cachedClientToken = token;
      return token;
    }
    return null;
  } catch {
    return null;
  }
}

export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const normalizedEndpoint = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;
  const url = `${publicEnv.NEXT_PUBLIC_API_BASE_URL}${normalizedEndpoint}`;

  const execute = async (tokenOverride?: string | null) => {
    const tokenToSend = tokenOverride ?? cachedClientToken;
    return fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(tokenToSend ? { "X-VeriMed-Client-Token": tokenToSend } : {}),
        ...(options?.headers ?? {}),
      },
    });
  };

  let response = await execute();
  if (response.status === 401 && normalizedEndpoint !== "/client-token") {
    cachedClientToken = null;
    const freshToken = await acquireAnonymousClientToken(
      publicEnv.NEXT_PUBLIC_API_BASE_URL
    );
    if (freshToken) {
      response = await execute(freshToken);
    }
  }

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMessage =
      payload?.error?.message ?? `HTTP Error ${response.status}`;
    const errorCode = payload?.error?.code ?? `HTTP_${response.status}`;
    throw new ApiClientError(errorMessage, response.status, errorCode);
  }

  return payload as T;
}
