# Security, Privacy, and Medical Safety — VeriMed (`docs/SAFETY.md`)

## 1. Medical Safety Boundaries

1. **Educational Evidence Tool, Not Medical Advice**:
   - VeriMed evaluates general public health claims against published scientific evidence.
   - VeriMed **never** diagnoses conditions, interprets individual lab results, or recommends personal treatment plans or dosages.
   - Every UI screen and API response carries a mandatory Bahasa Indonesia medical disclaimer:
     > *"VeriMed adalah alat bantu edukasi untuk memeriksa klaim kesehatan berdasarkan literatur ilmiah, bukan pengganti diagnosis, konsultasi, atau perawatan medis profesional."*
2. **Emergency Medical Interception**:
   - Submissions indicating acute medical distress (e.g., serangan jantung, sesak napas akut, gejala stroke, keracunan, percobaan bunuh diri) bypass the claim verification pipeline and display immediate instructions to contact **Layanan Darurat Medis 119** or visit the nearest **Instalasi Gawat Darurat (IGD)**.
3. **No Fabricated Citations or False Certainty**:
   - The system never invents citations, authors, or clinical studies.
   - When operating in development/mock mode (`AI_PROVIDER=mock`), all API responses set `is_demonstration: true` and the frontend displays a prominent warning that synthetic/demonstration mode is active.

---

## 2. AI & Application Security Controls

1. **Strict Groundedness & Citation Enforcement**:
   - User-submitted claims and retrieved document chunks are isolated in structured `<untrusted_evidence>` delimiters and screened for prompt-injection patterns.
   - `ProgrammaticCitationValidator` fails closed when non-empty evidence has zero citation markers, and `ConfigurableLLMAssessorExplainer` rejects ungrounded URLs/DOIs, invented years, or missing citations by falling back to deterministic grounded synthesis.
2. **Input Validation, Abuse Protection & Rate Limiting**:
   - Strict character limits and schema validation via Pydantic v2 (backend) and Zod (frontend), URL sanitization (`https:`-only `getSafeExternalUrl`), and Content-Security-Policy with per-request nonces in `apps/web`.
   - Trusted-proxy-aware sliding-window rate limiting with route-tier caps, concurrency semaphores (`MAX_CONCURRENT_VERIFICATIONS`), and LLM daily call budgets/circuit breakers (`LLM_DAILY_CALL_BUDGET`).
   - Short-lived signed `feedback_token` binding + `client-token`/API key controls (`REQUIRE_CLIENT_AUTH`).
3. **SSRF Protection**:
   - All ingested documents (including `is_synthetic_demo=true`) enforce HTTPS-only URL validation rejecting userinfo credentials, non-443 ports, obfuscated/mapped private IPs, and DNS resolution to non-public networks when fetching externally.
4. **Secrets, Host Header & CORS Isolation**:
   - Production startup fails fast if database URLs, `CLIENT_AUTH_SECRET`, or `FEEDBACK_TOKEN_SECRET` are missing or contain insecure defaults. `TrustedHostMiddleware` enforces `ALLOWED_HOSTS` and OpenAPI docs are disabled by default in `staging`/`production`.
5. **Privacy by Default**:
   - `verification_requests.is_private` defaults to `TRUE` with at-rest claim redaction (`ANONYMIZE_PRIVATE_CLAIMS=true`) and retention cleanup (`scripts/purge_expired_verifications.py`).
   - Frontend local history stores only 24h TTL redacted metadata unless the user explicitly opts in.
   - Security telemetry logs structured JSON events to `verimed_api.security` without logging raw health claims or secrets.
