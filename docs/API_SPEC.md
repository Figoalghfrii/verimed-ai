# API Specification — VeriMed (`docs/API_SPEC.md`)

**Base Path**: `/api/v1`  
**Content-Type**: `application/json`

---

## 1. Standard Response Envelopes

All API endpoints return a consistent JSON structure so frontend clients and automated tests can parse responses deterministically.

### Success Envelope (`ApiResponse<T>`)
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-10-31T05:00:00Z",
    "api_version": "v1",
    "is_demonstration": true
  }
}
```

### Error Envelope (`ErrorResponse`)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed.",
    "details": [
      {
        "field": "claim_text",
        "issue": "String should have at least 10 characters"
      }
    ]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-10-31T05:00:00Z",
    "api_version": "v1",
    "is_demonstration": true
  }
}
```

---

## 2. Phase 1 Implemented Endpoints

### `GET /api/v1/health/live`
Unprivileged liveness probe exempt from rate limiting (returns `{ "status": "ok" }` with no database queries or operational metadata). Use this endpoint for container health checks.

### `GET /api/v1/health`
Checks service readiness, database connectivity, and `pgvector` extension readiness (rate-limited). In `staging` and `production` (`EXPOSE_OPERATIONAL_METADATA=false`), `version`, `environment`, `ai_provider`, and `database.latency_ms` are omitted (`null`).

### `POST /api/v1/client-token`
Issues a short-lived HMAC-signed anonymous browser token (`X-VeriMed-Client-Token`) validating `Origin` against `CORS_ORIGINS`. When `REQUIRE_CLIENT_AUTH=true` (default in `staging`/`production`), `POST /api/v1/verify` and `POST /api/v1/feedback` require either `X-API-Key` or `X-VeriMed-Client-Token`.

#### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "VeriMed API",
    "version": "0.1.0",
    "environment": "development",
    "ai_provider": "mock",
    "database": {
      "status": "connected",
      "pgvector_enabled": true,
      "latency_ms": 2.4
    },
    "disclaimer": "VeriMed adalah platform edukasi verifikasi klaim kesehatan berbasis bukti, bukan alat diagnosis medis."
  },
  "meta": {
    "request_id": "8f9d2a1b-3c4e-4f5a-9b1c-2d3e4f5a6b7c",
    "timestamp": "2026-10-31T05:15:00Z",
    "api_version": "v1",
    "is_demonstration": true
  }
}
```

---

## 3. Phase 2 Implemented Verification Endpoint

### `POST /api/v1/verify`
Evaluates a submitted health claim (`language`: `"id"` or `"en"`) through the VeriMed verification pipeline (`mock`, `hybrid`, or `configurable` via `AI_PROVIDER`), returning explanations, emergency guidance, and disclaimers in the requested language.

#### Request Body
```json
{
  "text": "Minum air rebusan daun sirsak dapat menyembuhkan semua jenis kanker tanpa kemoterapi.",
  "language": "id"
}
```

#### Response `200 OK`
Returns `ApiResponse[VerificationResponseData]`:
- `status`: `"COMPLETED"` or `"EMERGENCY_HALT"`
- `is_demonstration`: `true` when `AI_PROVIDER=mock`
- `persisted`: `true` if persisted to PostgreSQL, `false` if running stateless when DB is offline
- `emergency_triggered`: `true` when acute emergency indicators are detected (returns `emergency_guidance` with **119 / IGD** contacts and empty `claims`)
- `claims[]`: list of extracted claims with optional `assessment_id` (UUID returned when `persisted=true`), `verdict`, `verdict_label_id`, `confidence_score`, `abstained`, `explanation`, `uncertainty_notes`, `citations_valid`, and `sources[]` (`is_synthetic_demo: true` in mock mode)
- `disclaimer`: mandatory Bahasa Indonesia non-diagnostic disclaimer
- `feedback_token`: server-signed HMAC token required when submitting `POST /api/v1/feedback` (`null` on emergency halt)

#### Assessment Verdicts
- `SUPPORTED` (*Didukung Bukti*)
- `CONTRADICTED` (*Bertentangan dengan Bukti*)
- `MIXED_EVIDENCE` (*Bukti Beragam*)
- `INSUFFICIENT_EVIDENCE` (*Bukti Tidak Cukup*)

---

## 4. Phase 3 Implemented Evidence Corpus Endpoint

### `GET /api/v1/evidence/stats`
Returns indexed evidence corpus counts (`documents_count`, `chunks_count`, `synthetic_documents_count`) along with the currently configured `ai_provider`, `embedding_backend`, and `reranker_backend`.

#### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "documents_count": 5,
    "chunks_count": 10,
    "synthetic_documents_count": 5,
    "ai_provider": "hybrid",
    "embedding_backend": "hash",
    "reranker_backend": "lexical"
  },
  "meta": {
    "request_id": "8f9d2a1b-3c4e-4f5a-9b1c-2d3e4f5a6b7c",
    "timestamp": "2026-10-31T05:15:00Z",
    "api_version": "v1",
    "is_demonstration": false
  }
}
```

---

## 5. Phase 4 Implemented User Feedback Endpoint & Rate Limiting

### `POST /api/v1/feedback`
Records anonymous user clarity ratings on verification explanations (`is_helpful`, optional `feedback_category` in `CLARITY | CITATIONS | ACCURACY_CONCERN | OTHER`, sanitized optional `comment` up to 500 characters, and valid `feedback_token`). Duplicate submissions for the same `(request_id, assessment_id)` pair return `409 DUPLICATE_FEEDBACK`; missing or tampered `feedback_token` returns `403 INVALID_FEEDBACK_TOKEN`.

#### Request Body
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_helpful": true,
  "feedback_category": "CLARITY",
  "comment": "Penjelasan ringkas dan mudah dipahami."
}
```

#### Response `201 Created`
```json
{
  "success": true,
  "data": {
    "feedback_id": "9f8e7d6c-5b4a-3210-fedc-ba9876543210",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_helpful": true,
    "feedback_category": "CLARITY",
    "persisted": true,
    "message": "Terima kasih! Masukan Anda membantu meningkatkan kejelasan penjelasan VeriMed."
  },
  "meta": {
    "request_id": "8f9d2a1b-3c4e-4f5a-9b1c-2d3e4f5a6b7c",
    "timestamp": "2026-11-21T17:00:00Z",
    "api_version": "v1",
    "is_demonstration": false
  }
}
```

### Rate-Limiting Middleware
Non-exempt endpoints include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers (controlled by `RATE_LIMIT_ENABLED`, `RATE_LIMIT_REQUESTS_PER_MINUTE`, and stricter route limits on `/verify`, `/feedback`, and `/client-token`). Client IPs are extracted via direct socket peer or rightmost untrusted `X-Forwarded-For` hop when peer IP is in `TRUSTED_PROXIES`, backed by an LRU-bounded bucket store. Only `/api/v1/health/live` stays exempt from throttling.

---

## 6. Phase 6 Implemented Corpus Explorer & Feedback Analytics Endpoints

### `GET /api/v1/evidence/documents`
Returns paginated metadata for indexed curated and synthetic demonstration documents (`items`, `total`, `limit`, `offset`, `database_connected`). Supports optional query parameters:
- `q` (max 120 chars): case-insensitive substring filter over document `title` and `source_name`.
- `source_type` (max 64 chars): exact filter such as `OFFICIAL_GUIDELINE`, `WHO_FACT_SHEET`, `WHO_GUIDANCE`, `BPOM_ADVISORY`, or `SYNTHETIC_DEMO_GUIDELINE`.
- `include_synthetic` (`true`/`false`, default `true`): excludes synthetic demo documents when `false`.
- `limit` (`1–50`, default `20`) and `offset` (`>= 0`, default `0`).

### `GET /api/v1/feedback/stats`
Returns aggregated anonymous user clarity feedback counts (`total_count`, `helpful_count`, `not_helpful_count`, `helpful_rate`, `by_category`, `database_connected`) without exposing raw user comments.
