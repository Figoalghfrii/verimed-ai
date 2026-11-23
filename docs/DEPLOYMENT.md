# Deployment & Production Operations Guide — VeriMed (`docs/DEPLOYMENT.md`)

## 1. Prerequisites
- **Docker** and **Docker Compose v2**
- Production `.env` derived from `.env.example` (never commit `.env` to Git)

---

## 2. Production Environment Hardening

Before running in staging or production, update `.env`:
1. **`APP_ENV=production`** and strong unique passwords for `POSTGRES_PASSWORD` (owner/migrations) and `POSTGRES_APP_PASSWORD` (least-privilege runtime `verimed_app` role).
2. **`CLIENT_AUTH_SECRET` & `FEEDBACK_TOKEN_SECRET`**: set cryptographically random secrets (>= 32 chars). In `staging`/`production`, startup fails fast if insecure placeholders (`verimed_dev_password`) or missing secrets are detected.
3. **`ALLOWED_HOSTS` & `CORS_ORIGINS`**: set explicit allowed hostnames and frontend origin(s), e.g. `["https://verimed.example.com"]`, and `TRUSTED_PROXIES` CIDR blocks when running behind a reverse proxy.
4. **`NEXT_PUBLIC_API_BASE_URL`**: set to the public HTTPS URL of the FastAPI API (`https://...` enforced in non-local production builds).
5. **`AI_PROVIDER`**:
   - `hybrid`: uses PostgreSQL `pgvector` + `tsvector` hybrid retrieval with deterministic grounded assessment.
   - `configurable`: enables external OpenAI-compatible grounded synthesis via `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL_NAME` bounded by `LLM_DAILY_CALL_BUDGET`.
6. **Hardened Runtime Defaults**: keep `RATE_LIMIT_ENABLED=true`, `EXPOSE_API_DOCS=false`, `EXPOSE_OPERATIONAL_METADATA=false`, and schedule periodic retention cleanup via `scripts/purge_expired_verifications.py`.

---

## 3. External LLM Setup — Google Gemini (OpenAI-Compatible)

VeriMed supports Google Gemini natively through `AI_PROVIDER=configurable` using Google's OpenAI-compatible Chat Completions endpoint (`ConfigurableLLMAssessorExplainer`).

1. Generate an API key in **Google AI Studio**.
2. Copy `.env.example` to `.env` (gitignored) and configure:
   ```env
   AI_PROVIDER=configurable
   EMBEDDING_BACKEND=sentence_transformers
   RERANKER_BACKEND=cross_encoder
   LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
   LLM_API_KEY=<paste-your-gemini-api-key>
   LLM_MODEL_NAME=gemini-2.5-flash
   ```
3. Rebuild / restart the API container (`docker compose up -d --build`) or local Uvicorn server.
   - If the Gemini quota/network fails or `LLM_API_KEY` is blank, VeriMed safely falls back to deterministic `HybridGroundedAssessor` / `HybridGroundedExplainer` while preserving hard abstention (`INSUFFICIENT_EVIDENCE`) and citation validation (`[n]`).

---

## 4. Container Build & Startup

Validate Compose configuration and build production images (use `--build-arg INSTALL_ML=true` if running `sentence_transformers` / `cross_encoder` inside the API container):
```powershell
docker compose config
docker compose build
docker compose up -d postgres api web
```

---

## 5. Database Migrations & Curated Corpus Seeding

Run Alembic migrations and ingest the verified Kemenkes RI / WHO / BPOM / NIH ODS corpus:
```powershell
docker compose exec api alembic upgrade head
```

From the repository root (using backend virtualenv; add `--force-reembed` whenever switching between `EMBEDDING_BACKEND=hash` and `sentence_transformers`):
```powershell
.\apps\api\.venv\Scripts\python scripts\seed_demo_data.py --preset curated --force-reembed
```

---

## 6. Post-Deploy Verification Checklist
- `GET /api/v1/health/live` returns `200 OK` (`{"status": "ok"}`).
- `GET /api/v1/health` returns `status: "healthy"` and `pgvector_enabled: true` (operational metadata redacted in production).
- `GET /api/v1/evidence/stats` confirms indexed curated documents and chunks (`> 0`).
- `GET /api/v1/evidence/documents?include_synthetic=false` lists curated sources.
- `GET /api/v1/feedback/stats` returns `database_connected: true`.
- Open `/verify` and `/corpus` in the browser and verify medical disclaimers and emergency interception (`119`).
