import {
  VerificationResponseData,
  VerificationResponseDataSchema,
} from "../schemas/verification-schema";

const HISTORY_STORAGE_KEY = "verimed_verification_history_v1";
const MAX_HISTORY_ITEMS = 5;

export interface VerificationHistoryEntry {
  saved_at: string;
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
    for (const item of parsed) {
      if (
        typeof item === "object" &&
        item !== null &&
        "saved_at" in item &&
        typeof item.saved_at === "string" &&
        "result" in item
      ) {
        const resultCheck = VerificationResponseDataSchema.safeParse(item.result);
        if (resultCheck.success) {
          validEntries.push({
            saved_at: item.saved_at,
            result: resultCheck.data,
          });
        }
      }
    }
    return validEntries.slice(0, MAX_HISTORY_ITEMS);
  } catch {
    return [];
  }
}

export function saveVerificationToHistory(
  result: VerificationResponseData
): VerificationHistoryEntry[] {
  if (typeof window === "undefined" || result.emergency_triggered) {
    return loadVerificationHistory();
  }

  const current = loadVerificationHistory().filter(
    (entry) => entry.result.request_id !== result.request_id
  );
  const next: VerificationHistoryEntry[] = [
    { saved_at: new Date().toISOString(), result },
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
