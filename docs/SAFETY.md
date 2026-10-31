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

1. **Untrusted Input & Prompt Injection Mitigation**:
   - Both user-submitted claims and retrieved document chunks are treated as untrusted input.
   - Retrieved passages are isolated in structured XML-like delimiters (`<untrusted_evidence>`) and never concatenated raw into system instructions.
2. **Input Validation & Rate Limiting**:
   - Strict character limits and schema validation via Pydantic v2 (backend) and Zod (frontend).
   - Rate-limiting headers and IP-based request throttling hooks are designed into the API middleware layer.
3. **SSRF Protection**:
   - Phase 1 accepts plain text claims only. Before any future URL ingestion is enabled, strict allowlisting of trusted domains and private IP range blocking (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`) are enforced.
4. **Secrets & CORS Isolation**:
   - Backend credentials and API keys remain exclusively in server-side environment variables.
   - CORS origins are explicitly configured via `CORS_ORIGINS`.
5. **Privacy by Default**:
   - `verification_requests.is_private` defaults to `TRUE`.
   - Application logs record request IDs, status codes, and latency without logging raw user health text in production logs.
