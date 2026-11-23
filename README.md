# VeriMed (`verimed-ai`)

> **Verify Health. Trust Evidence.**  
> AI-Powered Health Claim Verification and Evidence Intelligence Platform for the Indonesian General Public.  
> Aligned with **UN Sustainable Development Goal 3 (Good Health and Well-Being)**.

---

## 1. Overview

Health misinformation spreads rapidly across social media and messaging platforms. **VeriMed** helps users critically evaluate health claims in **Bahasa Indonesia** through hybrid evidence retrieval, calibrated stance assessment (`Supported`, `Contradicted`, `Mixed Evidence`, `Insufficient Evidence`), grounded explanations with verifiable citations, and explicit uncertainty communication.

> **Important Medical Disclaimer**: VeriMed is an educational evidence-assistance platform, **not** a clinical diagnostic system or medical advice service.

---

## 2. Tech Stack

- **Frontend (`apps/web`)**: Next.js (App Router), TypeScript, Tailwind CSS, TanStack Query v5, Zod, Vitest
- **Backend (`apps/api`)**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, Pytest, Ruff
- **Database**: PostgreSQL 16 + `pgvector` (semantic vector search) + `pg_trgm` / `tsvector` (lexical search)
- **ML Workspace (`ml/`)**: Offline evaluation and embedding experimentation workspace
- **Infrastructure**: Docker & Docker Compose

---

## 3. Repository Structure

```text
verimed-ai/
├── .agents/rules/          # Antigravity project rules
├── apps/
│   ├── web/                # Next.js frontend application
│   └── api/                # FastAPI modular monolith backend
├── ml/                     # Offline ML research & evaluation workspace
├── infra/docker/           # Dockerfiles & PostgreSQL pgvector init scripts
├── docs/                   # PRD, Architecture, Database, API, Pipeline, Safety, Roadmap
├── scripts/                # Health check and operational scripts
├── AGENTS.md               # Root agent guidelines
├── compose.yaml            # Local PostgreSQL + API + Web orchestration
└── .env.example            # Environment variable template
```

---

## 4. Quick Start & Local Development

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 20+ (and `npm`)
- **Docker & Docker Compose**: For PostgreSQL 16 with `pgvector`

### Step 1: Environment Configuration
Copy `.env.example` to `.env` in the repository root:
```powershell
Copy-Item .env.example .env
```

### Step 2: Start PostgreSQL with `pgvector`
```powershell
docker compose up -d postgres
```

### Step 3: Set Up & Run Backend (`apps/api`)
```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Optional: install local sentence-transformers ML models for Phase 3 embeddings/reranking
# pip install -e ".[ml]"

# Run Alembic database migrations
alembic upgrade head

# Optional (Phase 3 / Phase 5): seed curated public health or synthetic evidence into PostgreSQL
# cd ..\..
# .\apps\api\.venv\Scripts\python scripts\seed_demo_data.py --preset curated
# .\apps\api\.venv\Scripts\python scripts\seed_demo_data.py --preset synthetic
# cd apps\api

# Start FastAPI server on http://localhost:8000
uvicorn verimed_api.main:app --reload --host 0.0.0.0 --port 8000
```

- **Health Endpoint**: `http://localhost:8000/api/v1/health`
- **Evidence Corpus Stats**: `http://localhost:8000/api/v1/evidence/stats`
- **Interactive OpenAPI Docs**: `http://localhost:8000/api/v1/docs`

> Set `AI_PROVIDER=hybrid` (or `AI_PROVIDER=configurable` with `LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai` + `LLM_API_KEY` + `LLM_MODEL_NAME=gemini-2.5-flash` for Google Gemini) in `.env` to verify claims against the seeded PostgreSQL `pgvector` + `tsvector` hybrid retriever instead of the default `mock` demo provider. Add `--force-reembed` to `seed_demo_data.py` whenever switching `EMBEDDING_BACKEND`.

### Step 4: Set Up & Run Frontend (`apps/web`)
In a separate terminal:
```powershell
cd apps/web
npm install
npm run dev
```
Open `http://localhost:3000` in your browser to view the VeriMed landing page and live Backend + `pgvector` connectivity status panel.

---

## 5. Testing, Linting & Type Checking

### Backend (`apps/api`)
```powershell
cd apps/api
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m pytest -v
```

### Offline ML Evaluation (`ml/evaluation/`)
```powershell
.\apps\api\.venv\Scripts\python ml\evaluation\run_evaluation.py
.\apps\api\.venv\Scripts\python -m pytest ml\evaluation\test_evaluation_metrics.py -v
```

### Frontend (`apps/web`)
```powershell
cd apps/web
npm run typecheck
npm run lint
npm test
npm run test:e2e
npm run build
```

---

## 6. Documentation Index

- [Product Requirements Document (PRD)](./docs/PRD.md)
- [Software Architecture](./docs/ARCHITECTURE.md)
- [Database Schema & Entities](./docs/DATABASE.md)
- [API Specification](./docs/API_SPEC.md)
- [AI Verification Pipeline Design](./docs/AI_PIPELINE.md)
- [Security, Privacy & Medical Safety](./docs/SAFETY.md)
- [Development Roadmap](./docs/ROADMAP.md)
- [Deployment & Production Operations](./docs/DEPLOYMENT.md)
