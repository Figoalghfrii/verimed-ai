/** URL sanitization helper ensuring only safe HTTPS external links are rendered. */

const ALLOWED_EXTERNAL_PROTOCOLS = new Set(["https:"]);

export function getSafeExternalUrl(rawUrl: string | null | undefined): string | null {
  if (!rawUrl) {
    return null;
  }
  const trimmed = rawUrl.trim();
  if (!trimmed || trimmed.length > 2048 || /[\s\u0000-\u001f]/.test(trimmed)) {
    return null;
  }

  try {
    const parsed = new URL(trimmed);
    if (!ALLOWED_EXTERNAL_PROTOCOLS.has(parsed.protocol)) {
      return null;
    }
    if (parsed.username || parsed.password) {
      return null;
    }
    return parsed.toString();
  } catch {
    return null;
  }
}
