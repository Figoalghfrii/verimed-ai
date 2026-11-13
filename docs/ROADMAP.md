# Development Roadmap — VeriMed (`docs/ROADMAP.md`)

## Phase 1: Project Foundation (Current Phase)
- [x] Initialize monorepo directory structure (`apps/web`, `apps/api`, `ml`, `infra/docker`, `docs`, `.agents/rules`).
- [x] Author architecture, PRD, database, API, AI pipeline, and safety specifications.
- [x] Configure PostgreSQL 16 with `pgvector` and `pg_trgm` extensions in Docker Compose.
- [x] Scaffold FastAPI backend with SQLAlchemy 2.0 async ORM and Alembic migrations for all 9 core tables.
- [x] Implement standardized API response/error envelopes and `GET /api/v1/health` with live database + `pgvector` checks.
- [x] Scaffold Next.js App Router frontend (TypeScript, Tailwind CSS, TanStack Query, Zod) with live backend connectivity verification page in Bahasa Indonesia.
- [x] Configure linting, formatting, and automated unit/integration tests (`pytest`, `ruff`, `vitest`, `eslint`).

## Phase 2: Core Verification MVP & Deterministic Pipeline (Current Phase)
- [x] Implement modular AI pipeline stages (`SafetyGuard`, `ClaimExtractor`, `QueryNormalizer`, `Retriever`, `Reranker`, `Assessor`, `Explainer`, `CitationValidator`, `Orchestrator`).
- [x] Implement deterministic demonstration provider with clearly labeled synthetic evidence for local development.
- [x] Build `POST /api/v1/verify` endpoint and persistence repositories.
- [x] Build interactive Claim Verification UI (`/verify`) and Methodology page (`/about`) with source cards, verdict badges, uncertainty callouts, and emergency safety banner.

## Phase 3: Curated Evidence Ingestion & Hybrid Retrieval
- [ ] Build reproducible ingestion scripts for trusted public health sources (WHO, Kemenkes RI, BPOM, open-access biomedical summaries).
- [ ] Integrate local multilingual embedding generation (`intfloat/multilingual-e5-base`) and `pgvector` HNSW indexing + PostgreSQL `tsvector` lexical search.
- [ ] Integrate cross-encoder reranking and configurable grounded LLM generation with citation validation.

## Phase 4: Evaluation, Hardening & User Feedback Loop
- [ ] Implement `POST /api/v1/feedback` for user clarity ratings.
- [ ] Execute retrieval Recall@K, stance Macro-F1, and citation fidelity evaluation suite in `ml/evaluation/`.
- [ ] Add end-to-end Playwright browser tests and rate-limiting middleware.
