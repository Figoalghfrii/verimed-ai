# VeriMed Backend API (`apps/api`)

FastAPI modular monolith backend for **VeriMed** (*Verify Health. Trust Evidence.*).

## Key Responsibilities
- Provides versioned REST endpoints (`/api/v1/*`) with standardized response envelopes.
- Manages PostgreSQL + `pgvector` schema via SQLAlchemy 2.0 Async and Alembic migrations.
- Enforces non-diagnostic medical safety disclaimers and zero-fabrication evidence guarantees.
