---
trigger: always_on
description: Enforces VeriMed modular monolith boundaries, separation of concerns, and documentation synchronization.
---

# Architecture Consistency Rules

1. **Monorepo Directory Structure**:
   - Keep frontend code exclusively in `apps/web/`.
   - Keep backend production API and inference pipeline code exclusively in `apps/api/`.
   - Keep offline ML experimentation, datasets, and benchmarks in `ml/`.
   - Keep containerization configs in `infra/docker/` and `compose.yaml`.
   - Keep architecture and engineering specifications in `docs/`.
2. **Strict Separation of Responsibilities**:
   - Do not import from `ml/` inside `apps/api/`.
   - Do not place business logic or direct SQL queries inside FastAPI route handlers (`apps/api/src/verimed_api/api/`).
   - Do not perform direct database queries from `apps/web/`. All frontend data access goes through versioned REST API endpoints (`/api/v1/*`).
3. **Incremental & Reviewable Changes**:
   - Make small, focused changes with clear boundaries.
   - Do not introduce microservices, message brokers, or distributed queues unless explicitly requested and documented in `docs/ARCHITECTURE.md`.
4. **Documentation Synchronization**:
   - Any modification to database tables, API endpoints, or pipeline stages must be reflected in `docs/DATABASE.md`, `docs/API_SPEC.md`, or `docs/AI_PIPELINE.md`.
