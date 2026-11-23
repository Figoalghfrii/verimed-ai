import {
  VerificationResponseData,
  VerificationResponseDataSchema,
} from "../schemas/verification-schema";

const HISTORY_STORAGE_KEY = "verimed_verification_history_v1";
const MAX_HISTORY_ITEMS = 5;

export interface VerificationHistoryEntry {
  saved_at: string;
  expires_at?: string;
  claim_text_saved?: boolean;
  result: VerificationResponseData;
}

export function formatWhatsAppSummary(
  result: VerificationResponseData
): string {
  const lines: string[] = ["*VeriMed — Ringkasan Pemeriksaan Bukti*"];

  if (result.is_demonstration) {
    lines.push("_[Mode Demonstrasi / Data Simulasi]_");
  }

  for (const claim of result.claims) {
    const confidencePct = Math.round(claim.confidence_score * 100);
    lines.push("");
    lines.push(`*Klaim:* "${claim.claim_text}"`);
    lines.push(
      `*Penilaian:* ${claim.verdict_label_id} (${confidencePct}% keyakinan)`
    );
    lines.push(`*Penjelasan:* ${claim.explanation}`);

    if (claim.sources.length > 0) {
      lines.push("*Sumber Bukti:*");
      for (const source of claim.sources) {
        lines.push(
          `${source.citation_key} ${source.title} — ${source.source_name} (${source.source_url})`
        );
      }
    }
  }

  lines.push("");
  lines.push(`_Catatan: ${result.disclaimer}_`);
  return lines.join("\n");
}

export function loadVerificationHistory(): VerificationHistoryEntry[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    const validEntries: VerificationHistoryEntry[] = [];
    let prunedExpired = false;
    for (const item of parsed) {
      if (
        typeof item === "object" &&
        item !== null &&
        "saved_at" in item &&
        typeof item.saved_at === "string" &&
        "result" in item
      ) {
        const expiresAt =
          "expires_at" in item && typeof item.expires_at === "string"
            ? item.expires_at
            : undefined;
        if (isHistoryExpired({ saved_at: item.saved_at, expires_at: expiresAt })) {
          prunedExpired = true;
          continue;
        }
        const resultCheck = VerificationResponseDataSchema.safeParse(item.result);
        if (resultCheck.success) {
          validEntries.push({
            saved_at: item.saved_at,
            expires_at: expiresAt,
            claim_text_saved:
              "claim_text_saved" in item && typeof item.claim_text_saved === "boolean"
                ? item.claim_text_saved
                : false,
            result: resultCheck.data,
          });
        }
      }
    }
    const trimmed = validEntries.slice(0, MAX_HISTORY_ITEMS);
    if (prunedExpired) {
      try {
        window.localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(trimmed));
      } catch {
        // Ignore storage write errors during expiry pruning
      }
    }
    return trimmed;
  } catch {
    return [];
  }
}

export interface SaveHistoryOptions {
  saveClaimText?: boolean;
  ttlHours?: number;
}

const DEFAULT_HISTORY_TTL_HOURS = 24;
const CLAIM_OPT_IN_KEY = "verimed_save_claim_text_opt_in";

export function isHistoryExpired(entry: { saved_at: string; expires_at?: string }): boolean {
  const now = Date.now();
  if (entry.expires_at) {
    const expiresMs = Date.parse(entry.expires_at);
    return Number.isNaN(expiresMs) || expiresMs <= now;
  }
  const savedMs = Date.parse(entry.saved_at);
  if (Number.isNaN(savedMs)) {
    return true;
  }
  return now - savedMs > DEFAULT_HISTORY_TTL_HOURS * 3600 * 1000;
}

export function loadClaimTextOptIn(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    return window.localStorage.getItem(CLAIM_OPT_IN_KEY) === "true";
  } catch {
    return false;
  }
}

export function saveClaimTextOptIn(enabled: boolean): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    if (enabled) {
      window.localStorage.setItem(CLAIM_OPT_IN_KEY, "true");
    } else {
      window.localStorage.removeItem(CLAIM_OPT_IN_KEY);
    }
  } catch {
    // Ignore storage access errors cleanly
  }
}

export function redactResultForLocalHistory(
  result: VerificationResponseData,
  saveClaimText: boolean
): VerificationResponseData {
  if (saveClaimText) {
    return result;
  }
  return {
    ...result,
    claims: result.claims.map((claim) => ({
      ...claim,
      claim_text: "[Disembunyikan demi privasi — aktifkan opsi simpan klaim untuk melihat teks]",
      normalized_query: "",
      explanation: `Ringkasan lokal hanya menyimpan status penilaian (${claim.verdict_label_id}).`,
      uncertainty_notes: claim.uncertainty_notes,
    })),
  };
}

export function saveVerificationToHistory(
  result: VerificationResponseData,
  options: SaveHistoryOptions = {}
): VerificationHistoryEntry[] {
  if (typeof window === "undefined" || result.emergency_triggered) {
    return loadVerificationHistory();
  }

  const saveClaimText = options.saveClaimText ?? loadClaimTextOptIn();
  const ttlHours = options.ttlHours ?? DEFAULT_HISTORY_TTL_HOURS;
  const now = new Date();
  const expiresAt = new Date(now.getTime() + ttlHours * 3600 * 1000).toISOString();
  const storedResult = redactResultForLocalHistory(result, saveClaimText);

  const current = loadVerificationHistory().filter(
    (entry) => entry.result.request_id !== result.request_id
  );
  const next: VerificationHistoryEntry[] = [
    {
      saved_at: now.toISOString(),
      expires_at: expiresAt,
      claim_text_saved: saveClaimText,
      result: storedResult,
    },
    ...current,
  ].slice(0, MAX_HISTORY_ITEMS);

  try {
    window.localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Ignore storage quota or private browsing errors cleanly
  }
  return next;
}

export function clearVerificationHistory(): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.removeItem(HISTORY_STORAGE_KEY);
  } catch {
    // Ignore storage access errors cleanly
  }
}
