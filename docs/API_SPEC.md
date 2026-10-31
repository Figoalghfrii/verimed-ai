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

### `GET /api/v1/health`
Checks service liveness, database connectivity, and `pgvector` extension readiness.

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

## 3. Planned Phase 2 Verification Endpoint Contract

### `POST /api/v1/verify` (Planned for Next Phase)
Evaluates a submitted health claim through the VeriMed pipeline.

#### Request Body
```json
{
  "text": "Minum air rebusan daun sirsak dapat menyembuhkan semua jenis kanker tanpa kemoterapi.",
  "language": "id"
}
```

#### Assessment Verdicts
- `SUPPORTED` (*Didukung Bukti*)
- `CONTRADICTED` (*Bertentangan dengan Bukti*)
- `MIXED_EVIDENCE` (*Bukti Beragam*)
- `INSUFFICIENT_EVIDENCE` (*Bukti Tidak Cukup*)
