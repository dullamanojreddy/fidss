# FIDSS Agent Operating Rules

These rules are non-negotiable standards for any human engineer or AI coding agent working on the FIDSS codebase.

## 1. Core Operating Principles
1. **Read Before Coding**: Always read `docs/PROJECT_CONTEXT.md` and `AGENT_RULES.md` before generating or modifying any code.
2. **Strict Ownership Boundaries**: Each person/agent has exclusive write ownership over designated folders. Never write to or modify another person's folder.
   - **Person 1 (OCR, Preprocessing & Quality)**: `backend/app/modules/ocr/`, `backend/app/modules/quality/`, `frontend/src/components/OcrOverlay.jsx`
   - **Person 2 (Validation, MRZ & Watchlist)**: `backend/app/modules/validation/`, `backend/app/providers/watchlist/local_provider.py`, `backend/rules/`, `frontend/src/components/MrzResultCard.jsx`, `frontend/src/components/ValidationChecklist.jsx`
   - **Person 3 (Forensics / CV Tampering)**: `backend/app/modules/tampering/`, `frontend/src/components/TamperFindingsPanel.jsx`
   - **Person 4 (Face & Fusion)**: `backend/app/modules/face/`, `backend/app/modules/fusion/`, `frontend/src/components/FaceMatchCard.jsx`, `frontend/src/components/RiskScoreBadge.jsx`
   - **Person 5 (Platform, Backend, Orchestrator & Frontend Shell)**: `backend/app/core/`, `backend/app/db/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/providers/`, `backend/app/api/`, `frontend/` (shell, pages, layouts, api, context, router), `docker-compose.yml`, `docs/`, `tests/`
3. **No Cross-Module Bug "Fixing"**: If an analytical module returns data that fails schema validation:
   - Person 5 does **not** rewrite or patch that module's internal code.
   - Person 5 flags a **CONTRACT VIOLATION** and records `ModuleResult.status = FAILED` or `INCONCLUSIVE`.
   - The respective module owner (P1–P4) is responsible for fixing their algorithm.
4. **Contract-Driven Development**:
   - `backend/app/schemas/` defines the immutable contract.
   - Modules must accept `DocumentContext` and return `ModuleResult`.
   - Never change shared schemas without formal documentation in `PROJECT_CONTEXT.md` and contract test updates.
5. **Database-Driven Architecture**:
   - Do **NOT** hardcode static data into the frontend or backend mock returns. All data must be modeled, persisted in the database, and served through REST endpoints.
6. **Failure Isolation & Non-Negotiable Invariants**:
   - A module failure, timeout, or missing check must **NEVER** silently produce a `CLEAR` verdict.
   - Incomplete or failed checks must escalate to `REVIEW_RECOMMENDED` or `INCONCLUSIVE`.
   - `NO_FACE` or low image quality must **NEVER** be converted into a fraudulent `MISMATCH`.
7. **No Hardcoded Secrets**:
   - Passwords, JWT keys, and credentials must strictly be loaded from environment variables (`.env`).
8. **Cryptographic Audit Integrity**:
   - All critical actions (`SCREENING_CREATED`, `FINDING_CREATED`, `OFFICER_REVIEWED`, `REPORT_GENERATED`, `SYSTEM_SETTING_CHANGED`) must be hashed into the SHA-256 chain.
   - The chain is tamper-evident. Any mutation in history must cause audit verification failure.
9. **Update Documentation**:
   - Update `docs/PROJECT_CONTEXT.md` whenever adding features, endpoints, or database models.
10. **Test Coverage**:
    - Every service, schema, and API endpoint must have automated tests. Run tests before committing.
