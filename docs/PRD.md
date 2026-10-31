# Product Requirements Document (PRD) — VeriMed

**Project Name**: VeriMed (`verimed-ai`)  
**Tagline**: *Verify Health. Trust Evidence.*  
**Target Audience**: Indonesian General Public  
**Primary UI Language**: Bahasa Indonesia  
**SDG Alignment**: UN Sustainable Development Goal 3 (Good Health and Well-Being)

---

## 1. Product Objectives

1. **Counter Health Misinformation**: Empower everyday users in Indonesia to evaluate viral health claims circulating on messaging apps and social media against curated, trustworthy medical evidence.
2. **Evidence-Grounded Explanations**: Translate complex biomedical literature and official health guidance into accessible Bahasa Indonesia explanations backed by transparent citations.
3. **Calibrated Uncertainty & Abstention**: Clearly communicate when scientific evidence is mixed or insufficient rather than guessing or overstating certainty.
4. **User Safety First**: Maintain strict boundaries as an educational evidence-intelligence platform—never acting as a clinical diagnostic or prescribing tool, and intercepting acute medical emergencies with immediate emergency hotline guidance (119 / IGD).

---

## 2. User Personas

### Persona 1: Sari (Family Caregiver, 38, Surabaya)
- **Context**: Frequently receives forwarded WhatsApp messages about herbal remedies, vaccine claims, and dietary cures in family groups.
- **Need**: Wants a fast, clear Bahasa Indonesia summary showing whether Kementerian Kesehatan RI / WHO / clinical studies support or contradict a claim before sharing or acting on it.

### Persona 2: Andi (University Student & Science Communicator, 22, Bandung)
- **Context**: Fact-checks health claims on social media and needs primary source links and nuanced context when studies disagree.
- **Need**: Direct links to supporting and contradicting sources, publication dates, and explicit limitations of the retrieved studies.

### Persona 3: Budi (Public Health Researcher, 31, Jakarta)
- **Context**: Evaluates automated claim verification pipelines for Indonesian public health literacy.
- **Need**: Reproducible architecture, clear separation between retrieval scores and stance classification, and strict citation fidelity.

---

## 3. Functional Requirements

| ID | Feature | Description |
| :--- | :--- | :--- |
| **FR-01** | Claim Submission & Validation | Users submit free-text health claims (10–1,000 characters) in Bahasa Indonesia. Input is validated for length and safety. |
| **FR-02** | Emergency Interception | Input exhibiting acute medical emergency indicators triggers an immediate safety banner directing the user to call **119** or visit the nearest **IGD**. |
| **FR-03** | Atomic Claim Extraction | Compound text submissions are decomposed into distinct, verifiable health claims. |
| **FR-04** | Hybrid Evidence Retrieval | Queries curated evidence chunks using lexical (`tsvector`) + dense semantic (`pgvector`) retrieval and cross-encoder reranking. |
| **FR-05** | Calibrated Evidence Assessment | Classifies each claim into `SUPPORTED`, `CONTRADICTED`, `MIXED_EVIDENCE`, or `INSUFFICIENT_EVIDENCE`, abstaining when evidence quality is low. |
| **FR-06** | Grounded Explanation & Citations | Produces a Bahasa Indonesia explanation where every factual statement maps to a verified retrieved source chunk. |
| **FR-07** | Uncertainty & Disclaimer Display | Displays explicit uncertainty notes, source provenance cards, demonstration mode banners (when using mock providers), and a mandatory medical disclaimer. |
| **FR-08** | System Health Monitoring | Exposes `GET /api/v1/health` reporting API and PostgreSQL/`pgvector` operational status. |

---

## 4. Non-Functional Requirements

- **Reliability & Reproducibility**: Deterministic mock provider for offline development/CI; reproducible database migrations via Alembic.
- **Security & Privacy**: Verification requests are private by default (`is_private = true`), no unnecessary PII/PHI collection, strict CORS configuration, and prompt-injection isolation on retrieved text.
- **Accessibility**: Responsive mobile-first layout (WCAG 2.1 AA contrast, semantic landmarks, screen-reader friendly badges).
- **Maintainability**: Modular monolith separating Next.js (`apps/web`), FastAPI (`apps/api`), and offline ML research (`ml/`).

---

## 5. SDG 3 Alignment & Known Limitations

- **SDG 3 Alignment**: Directly supports Target 3.d (strengthening capacity for risk communication and public health literacy) and Target 3.4 (reducing premature mortality from non-communicable diseases through accurate prevention literacy).
- **Known Limitations**:
  1. Assessments reflect **only** the currently indexed evidence corpus, not the entirety of global medical knowledge.
  2. Does not evaluate personal medical histories, lab results, or individual symptoms.
  3. Phase 1 initializes foundational infrastructure and deterministic demonstration providers before production corpus ingestion.
