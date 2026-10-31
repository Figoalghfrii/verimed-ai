---
trigger: always_on
description: Enforces Python, FastAPI, SQLAlchemy 2.0, Pydantic v2, and security coding standards for apps/api.
---

# Backend Coding Standards (`apps/api`)

1. **Type Safety & Modern Python**:
   - Target Python 3.11+ with full type annotations on all function signatures and attributes.
   - Use Pydantic v2 (`BaseModel`, `ConfigDict`, `Field`) for all request/response schemas and settings.
   - Use SQLAlchemy 2.0 typed declarative syntax (`Mapped`, `mapped_column`) with async sessions (`AsyncSession`).
2. **API Design & Error Handling**:
   - Namespace all endpoints under `/api/v1`.
   - Return standardized response and error envelopes (`ApiResponse[T]`, `ErrorResponse`).
   - Validate and bound all user inputs (length limits, character sanitization).
3. **Security & Privacy**:
   - Never hardcode secrets, database passwords, or API keys. Read from environment variables via `verimed_api.core.config`.
   - Configure CORS origins explicitly; never use wildcard `*` with credentials in production.
   - Do not log raw personal health information (PHI) or sensitive user payloads in plain text logs.
   - Apply SSRF protections before adding any external URL fetching logic.
4. **Testing & Quality**:
   - Write `pytest` tests for every new endpoint, service, and schema validation rule.
   - Ensure `ruff check` and `ruff format --check` pass cleanly.
