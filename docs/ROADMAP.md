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
- [x] Build reproducible ingestion scripts for trusted public health sources (WHO, Kemenkes RI, BPOM, open-access biomedical summaries).
- [x] Integrate local multilingual embedding generation (`intfloat/multilingual-e5-base`) and `pgvector` HNSW indexing + PostgreSQL `tsvector` lexical search.
- [x] Integrate cross-encoder reranking and configurable grounded LLM generation with citation validation.

## Phase 4: Evaluation, Hardening & User Feedback Loop
- [x] Implement `POST /api/v1/feedback` for user clarity ratings.
- [x] Execute retrieval Recall@K, stance Macro-F1, and citation fidelity evaluation suite in `ml/evaluation/`.
- [x] Add end-to-end Playwright browser tests and rate-limiting middleware.

## Phase 5: Curated Public Health Corpus, UI Sync & CI/CD
- [x] Surface `GET /api/v1/evidence/stats` in the home connectivity dashboard and synchronize `/about` operational documentation.
- [x] Curate verified Kemenkes RI, WHO, and BPOM public health corpus (`ml/data/curated_public_health_corpus.json`) with `is_synthetic_demo: false`.
- [x] Add WhatsApp-ready shareable evidence summary copy button and privacy-safe local browser history in `/verify`.
- [x] Configure GitHub Actions CI workflow (`.github/workflows/ci.yml`) and verify Next.js production build.

## Phase 6: Corpus Explorer, Retrieval Audit & Production Readiness
- [x] Add `GET /api/v1/evidence/documents` and `/corpus` browser page with source filtering and search.
- [x] Persist `retrieval_results` audit rows in `VerificationRepository` and expand Indonesian medical synonyms (`campak`, `jamu`, `herbal`, `bko`, `diabetes`, `hipertensi`, `GGL`).
- [x] Add `GET /api/v1/feedback/stats` anonymous clarity summary, `/verify` language toggle (`id`/`en`), and curated sample pills.
- [x] Harden `api.Dockerfile`, `web.Dockerfile` (multi-stage production build), `compose.yaml`, and author `docs/DEPLOYMENT.md`.

## Phase 7: Bilingual Pipeline & Demo Parity
- [x] Expand `MockPipelineProvider` synthetic topics for full parity with `/verify` sample pills (`imunisasi`, `jamu`/`herbal`, `GGL`/`diabetes`/`hipertensi`).
- [x] Propagate `language` (`id` | `en`) through `SafetyGuard`, `IndonesianQueryNormalizer` cross-lingual synonyms, `VerificationPipelineOrchestrator`, grounded/LLM explainers, and disclaimers.
- [x] Add English sample claim chips and active local history selection highlight in `/verify`.

## Phase 8: Security Hardening, Privacy & Abuse Resistance
- [x] Make rate limiting trusted-proxy aware, add per-route quotas, LLM daily call budget, and concurrent verification semaphores.
- [x] Fail closed on citation validation and ungrounded LLM output; expand emergency-symptom lexicon and prompt-injection telemetry.
- [x] Add anonymous client-token / API-key access controls, signed single-use feedback tokens, and duplicate-feedback database constraints (`0002_security_hardening`).
- [x] Add privacy controls: at-rest claim redaction, retention purge script, 24h privacy-safe local history, and HTTPS-only external URL rendering.
- [x] Harden deployment: least-privilege `verimed_app` database role, read-only containers, required production secrets, CSP/security headers, dependency lockfile, and CI security/supply-chain gates.
