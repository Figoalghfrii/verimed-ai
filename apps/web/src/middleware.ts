import { NextRequest, NextResponse } from "next/server";

function resolveApiConnectOrigins(): string {
  const fallback = "http://localhost:8000 http://127.0.0.1:8000";
  const rawBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!rawBaseUrl) {
    return fallback;
  }
  try {
    const parsed = new URL(rawBaseUrl);
    if (process.env.NODE_ENV === "production") {
      return parsed.origin;
    }
    return `${parsed.origin} ${fallback}`;
  } catch {
    return process.env.NODE_ENV === "production" ? "" : fallback;
  }
}

export function middleware(request: NextRequest) {
  const nonceBytes = new Uint8Array(16);
  crypto.getRandomValues(nonceBytes);
  const nonce = btoa(String.fromCharCode(...nonceBytes));
  const isDev = process.env.NODE_ENV !== "production";
  const connectOrigins = resolveApiConnectOrigins();

  const cspDirectives = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}'${isDev ? " 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self' data:",
    `connect-src 'self' ${connectOrigins}`.trim(),
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
  ];
  const cspHeader = cspDirectives.join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", cspHeader);

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });

  response.headers.set("Content-Security-Policy", cspHeader);
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "no-referrer");
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()"
  );
  if (!isDev) {
    response.headers.set(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains"
    );
  }
  return response;
}

export const config = {
  matcher: [
    {
      source: "/((?!_next/static|_next/image|favicon.ico|icon.svg).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
