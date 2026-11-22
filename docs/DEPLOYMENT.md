# Deployment & Production Operations Guide — VeriMed (`docs/DEPLOYMENT.md`)

## 1. Prerequisites
- **Docker** and **Docker Compose v2**
- Production `.env` derived from `.env.example` (never commit `.env` to Git)

---

## 2. Production Environment Hardening

Before running in staging or production, update `.env`:
1. **`APP_ENV=production`** and strong PostgreSQL credentials (`POSTGRES_PASSWORD`).
2. **`CORS_ORIGINS`**: set explicit allowed frontend origin(s), e.g. `["https://verimed.example.com"]`.
3. **`NEXT_PUBLIC_API_BASE_URL`**: set to the public HTTPS URL of the FastAPI API (passed at build time to `infra/docker/web.Dockerfile`).
4. **`AI_PROVIDER`**:
   - `hybrid`: uses PostgreSQL `pgvector` + `tsvector` hybrid retrieval with deterministic grounded assessment.
   - `configurable`: enables external OpenAI-compatible grounded synthesis via `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL_NAME`.
5. **Rate Limiting**: keep `RATE_LIMIT_ENABLED=true` and tune `RATE_LIMIT_REQUESTS_PER_MINUTE` (default `60`).

---

## 3. Container Build & Startup

Validate Compose configuration and build production images:
```powershell
docker compose config
docker compose build
docker compose up -d postgres api web
```

---

## 4. Database Migrations & Curated Corpus Seeding

Run Alembic migrations and ingest the verified Kemenkes RI / WHO / BPOM corpus:
```powershell
docker compose exec api alembic upgrade head
```

From the repository root (using backend virtualenv or container):
```powershell
.\apps\api\.venv\Scripts\python scripts\seed_demo_data.py --preset curated
```

---

## 5. Post-Deploy Verification Checklist
- `GET /api/v1/health` returns `status: "healthy"` and `pgvector_enabled: true`.
- `GET /api/v1/evidence/stats` confirms indexed curated documents and chunks (`> 0`).
- `GET /api/v1/evidence/documents?include_synthetic=false` lists curated sources.
- `GET /api/v1/feedback/stats` returns `database_connected: true`.
- Open `/verify` and `/corpus` in the browser and verify medical disclaimers and emergency interception (`119`).
