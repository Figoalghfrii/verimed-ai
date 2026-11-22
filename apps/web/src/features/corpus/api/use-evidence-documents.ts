import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import {
  EvidenceDocumentListResponse,
  EvidenceDocumentListResponseSchema,
} from "../schemas/corpus-schema";

export interface EvidenceDocumentsQuery {
  q?: string;
  sourceType?: string;
  includeSynthetic?: boolean;
  limit?: number;
  offset?: number;
}

export async function fetchEvidenceDocuments(
  params: EvidenceDocumentsQuery = {}
): Promise<EvidenceDocumentListResponse> {
  const searchParams = new URLSearchParams();
  if (params.q && params.q.trim()) {
    searchParams.set("q", params.q.trim());
  }
  if (params.sourceType) {
    searchParams.set("source_type", params.sourceType);
  }
  if (params.includeSynthetic !== undefined) {
    searchParams.set("include_synthetic", String(params.includeSynthetic));
  }
  if (params.limit !== undefined) {
    searchParams.set("limit", String(params.limit));
  }
  if (params.offset !== undefined) {
    searchParams.set("offset", String(params.offset));
  }

  const queryStr = searchParams.toString();
  const endpoint = queryStr
    ? `/evidence/documents?${queryStr}`
    : "/evidence/documents";
  const raw = await apiFetch<unknown>(endpoint);
  return EvidenceDocumentListResponseSchema.parse(raw);
}

export function useEvidenceDocuments(params: EvidenceDocumentsQuery = {}) {
  return useQuery({
    queryKey: ["evidence-documents", params],
    queryFn: () => fetchEvidenceDocuments(params),
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
