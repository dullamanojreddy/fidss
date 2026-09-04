# FIDSS PROJECT CONTEXT

## 1. Project Overview
FIDSS (Fake Identity & Document Screening System) is a multi-layered identity document screening assistant engineered for high-throughput border checkpoints. FIDSS replaces slow, fatigue-prone manual document inspection with an explainable, evidence-backed decision support pipeline. FIDSS never acts as a black-box autonomous judge; every signal is captured as an `EvidenceItem` and presented with cryptographic traceability to an authorized border officer.

## 2. SIH Problem Statement
- **Problem Statement ID**: 26188 (Smart India Hackathon 2026)
- **Theme**: Blockchain & Cybersecurity / Smart Border Security
- **Target Challenges**: Forged passports/visas, altered dates of birth, photo replacement, copy-move tampering, tampered stamps, impersonation, synthetic/duplicate identities, expired documents, and blacklisted travelers.

## 3. Current Architecture
FIDSS is architected as a modular monolith:
- **Frontend**: React 18 + Vite + TailwindCSS single-page application with RBAC-guarded routes, real-time status display, interactive document & evidence inspection, and officer review workflows.
- **Backend API**: FastAPI (Python 3.11+) providing clean REST endpoints for auth, upload, orchestration, officer reviews, audit verification, dashboard metrics, and settings.
- **Orchestration**: 12-step sequential & isolated screening pipeline with pure contract boundaries and non-silent failure handling.
- **Database**: Relational storage (MySQL 8 in production with Alembic migrations; SQLite demo mode supported by configuration).
- **Audit Subsystem**: Tamper-evident SHA-256 hash-chained canonical event log with blockchain-ready anchor abstractions.

## 4. Technology Stack
- **Frontend**: React 18, Vite, TailwindCSS, React Router 6, Axios, Lucide React icons, Recharts
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn, Python-Jose (JWT), Passlib (Bcrypt)
- **Forensics & AI Engines (Owned by P1-P4)**: PaddleOCR PP-OCRv4, OpenCV, NumPy, Scikit-Image, PyWavelets, InsightFace (SCRFD + ArcFace), RapidFuzz
- **Deployment**: Docker Compose, Dockerfile (multi-stage build)

## 5. Folder Ownership & Team Division
- **Person 1**: OCR, Preprocessing & Quality (`backend/app/modules/ocr/`, `backend/app/modules/quality/`, `frontend/src/components/OcrOverlay.jsx`)
- **Person 2**: Validation, MRZ, Watchlist & Duplicate Identity (`backend/app/modules/validation/`, `backend/app/providers/watchlist/local_provider.py`, `backend/rules/`, `frontend/src/components/MrzResultCard.jsx`, `frontend/src/components/ValidationChecklist.jsx`)
- **Person 3**: Forensics & CV Tampering (`backend/app/modules/tampering/`, `frontend/src/components/TamperFindingsPanel.jsx`)
- **Person 4**: Face Verification & Evidence Fusion (`backend/app/modules/face/`, `backend/app/modules/fusion/`, `frontend/src/components/FaceMatchCard.jsx`, `frontend/src/components/RiskScoreBadge.jsx`)
- **Person 5 (Active Role)**: Platform, Backend Core, Database, Schemas, Orchestrator, Audit Hash Chain, APIs, Frontend Shell & Pages (`backend/app/core/`, `backend/app/db/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/providers/audit/`, `backend/app/api/`, `frontend/`, `docker-compose.yml`, `docs/`, `tests/`)

## 6. Shared Contracts
All modules communicate exclusively using Pydantic schemas in `backend/app/schemas/`:
- `DocumentContext`: Input context with image path, document type, SHA-256, and upstream module results.
- `ModuleResult`: Output from each module containing status (`SUCCESS`, `PARTIAL`, `FAILED`, `INCONCLUSIVE`), `EvidenceItem` array, execution metrics, and error metadata.
- `EvidenceItem`: Atomic evidence payload containing severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), confidence, description, bounding box coordinates, metrics, `module_name`, and `module_result_id` provenance.
- `QualityResult`: Usability status (`PASS`, `WARNING`, `FAIL`), blur, brightness, and resolution checks.
- `ScreeningResultResponse`: Consolidated screening verdict (`CLEAR`, `REVIEW_RECOMMENDED`, `ENHANCED_REVIEW_RECOMMENDED`, `INCONCLUSIVE`), overall risk score (0-100), and evidence breakdown.
- `OfficerReviewCreate` / `Response`: Formal officer decision recording (`ACCEPT`, `REJECT`, `ESCALATE`, `REQUEST_RECAPTURE`, `MARK_INCONCLUSIVE`).

## 7. Database Schema
Defined in `backend/app/models/`:
- `users`: Identity and RBAC credentials.
- `screenings`: Master screening sessions and verdicts.
- `documents`: Uploaded document metadata, mime types, file sizes, and SHA-256 hashes.
- `document_fields`: Extracted OCR and MRZ fields.
- `module_results`: Granular execution records per module.
- `evidence_items`: Relational evidence findings linked to screenings and module executions.
- `officer_reviews`: Human-in-the-loop decisions with timestamps and justification notes.
- `audit_logs`: Tamper-evident hash-chained event records.
- `system_settings`: Admin-managed thresholds and policy configurations.
- `model_registry`: Versioning, runtimes, and checksums for analytical models.

## 8. API Contracts
- `POST /api/auth/login`: Authenticate and obtain JWT token.
- `GET /api/auth/me`: Retrieve current authenticated officer/admin profile.
- `POST /api/screenings`: Upload identity document and initiate 12-step screening.
- `GET /api/screenings`: List screenings with status, risk score, and pagination.
- `GET /api/screenings/{id}`: Detailed screening data, module cards, and findings.
- `GET /api/screenings/{id}/evidence`: Normalized list of all evidence items.
- `GET /api/documents/{id}/file`: Securely stream preview image.
- `POST /api/screenings/{id}/review`: Submit officer verdict with audit event generation.
- `GET /api/audit/logs`: Retrieve hash-chained audit timeline.
- `POST /api/audit/{screening_id}/verify`: Verify audit trail cryptographic integrity.
- `POST /api/audit/tamper-demo`: Controlled demonstration of hash-chain tampering detection.
- `GET /api/dashboard`: Aggregated dashboard metrics and risk distributions.
- `GET /api/settings`: Fetch system settings and thresholds.
- `PUT /api/settings`: Update settings (Admin only, audited).
- `GET /api/watchlist/search`: Search synthetic watchlist records.

## 9. Module Status
- **P1 OCR & Quality**: Integration Ready (Stubs / Contract Conforming)
- **P2 Validation & MRZ**: Implemented & Tested (MRZ detection/parsing/checksum, India-specific rule engine, OCR↔MRZ cross-validation, synthetic watchlist + duplicate identity, all wired into `analyze()`. 59/59 relevant unit tests passing.)
- **P3 Tampering & Forensics**: Integration Ready (Stubs / Contract Conforming)
- **P4 Face & Fusion**: Integration Ready (Stubs / Contract Conforming)
- **P5 Platform & Integration**: Implemented (Complete database-driven platform)

## 10. Completed Work
- Frozen Pydantic data contracts in `backend/app/schemas/`.
- Full relational SQLAlchemy database schema with indexes and relationships.
- Complete 12-step screening orchestrator with `ModuleDispatcher` abstraction.
- Cryptographic SHA-256 audit hash-chain logger and verification engine.
- Complete FastAPI application with JWT auth, RBAC, and REST endpoints.
- Fully database-driven React 18 + TailwindCSS frontend reflecting the reference UI specification.
- MRZ detection, TD1/TD2/TD3 parsing, and ICAO 9303 weighted 7-3-1 checksum algorithm (verified against published check-digit test vectors) — `backend/app/modules/validation/`.
- India-specific document rule engine (passport, visa, national_id, driving_license, permit) — data-driven via `backend/rules/*/IND.json`, no hardcoded policy.
- OCR↔MRZ cross-validation for document-number/date/name mismatch detection.
- Synthetic watchlist matching (`LocalSyntheticWatchlistProvider`, clearly disclaimed prototype data) behind a swappable `WatchlistProvider` Protocol.
- Duplicate identity detection via normalized fuzzy name/DOB/document-number matching.
- `analyze()` entry point wiring all validation sub-checks together with per-step failure isolation — a single sub-check failing does not discard evidence already collected from other sub-checks, and never silently produces a false SUCCESS/CLEAR on missing input.

## 11. Current Work
- Verification of database persistence, API endpoints, audit verification demo, and UI integration.

## 12. Pending Tasks
- Final E2E test runs with curated clean and tampered document images.
- Integration tests when P1-P4 push algorithmic module implementations.
- Reconcile `context.ocr_result` field/key naming (e.g. `raw_lines`, `document_number`, `surname`, `given_names`, `date_of_birth`, `date_of_expiry`, `nationality`) between P2's assumptions and P1's actual OCR output once implemented.
- Wire `context.allowed_outputs["historical_records"]` with real historical screening data (DB query) before calling validation's `analyze()`, to activate duplicate identity detection (currently a safe no-op with empty default).

## 13. Known Bugs
- `test_audit_verification_and_tamper_detection` fails: `/api/audit/tamper-demo` does not appear to actually corrupt the hash chain — `verify` still returns `VERIFIED` after the tamper-demo call, expected `AUDIT_INTEGRITY_FAILURE`. (Found during P2 module testing; not caused by P2 changes.)
- `test_get_canonical_screening` and `test_submit_officer_review` fail with 404 on a fresh clone — demo screening `SID-2026-05-21-00124` doesn't exist. Section 17 references `SEED_ADMIN_PASSWORD`/`SEED_OFFICER_PASSWORD` env vars for seeding; possibly just a missing local `.env` setup step rather than a real bug — needs confirming.

## 14. Architecture Decisions
- **AD-001**: Decoupled orchestrator from ML libraries via `ModuleDispatcher` to allow seamless stubbing and independent team development.
- **AD-002**: Pure database-driven frontend; no mock arrays in React state.
- **AD-003**: Evidence provenance tracking linking each `EvidenceItem` to its generating `module_result_id`.
- **AD-004**: Strict failure invariant: failed or low-quality module execution transitions screening to `REVIEW_RECOMMENDED` or `INCONCLUSIVE`, never `CLEAR`.

## 15. Changed Files
- `AGENT_RULES.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ui-reference/ui-specification.md`
- `docs/architecture.md`, `docs/api-contracts.md`, `docs/database.md`, `docs/module-contracts.md`, `docs/security.md`, `docs/testing.md`, `docs/sop.md`
- `backend/app/core/*`
- `backend/app/db/*`
- `backend/app/models/*`
- `backend/app/schemas/*`
- `backend/app/services/*`
- `backend/app/providers/*`
- `backend/app/api/*`
- `frontend/*`
- `backend/app/modules/validation/*` (mrz_detector.py, mrz_parser.py, mrz_checksum.py, cross_validator.py, rule_engine.py, watchlist.py, duplicate_identity.py, config_loader.py, validation_config.json, analyze.py)
- `backend/app/providers/watchlist/*` (base.py, local_provider.py, synthetic_watchlist.json)
- `backend/rules/{passport,visa,national_id,driving_license,permit}/IND.json`
- `backend/tests/unit/test_analyze.py`, `test_cross_validator.py`, `test_mrz_checksum.py`, `test_mrz_detector.py`, `test_mrz_parser.py`, `test_rule_engine.py`, `test_watchlist_duplicate.py`
- `backend/requirements.txt` (added `rapidfuzz`)

## 16. Test Status
- Shared contracts tested against invalid inputs.
- Orchestrator tested against module crashes and partial execution.
- Audit hash-chain tested for tampering detection.
- Validation module: 59/59 tests passing across MRZ checksum/parser/detector, rule engine, cross-validator, watchlist/duplicate identity, and full `analyze()` integration. Includes failure-isolation tests (one sub-check failing doesn't discard other sub-checks' evidence) and a config-wiring test proving externalized thresholds actually affect behavior (not just present but unused).

## 17. Environment Status
- Demo and production environments configurable via `.env`.
- Database seeds created via environment variables (`SEED_ADMIN_PASSWORD`, `SEED_OFFICER_PASSWORD`).

## 18. Model Versions
- Model registry tracks versions for PaddleOCR PP-OCRv4, SCRFD 10G, and ArcFace ResNet50.

## 19. Demo Status
- Reproducible demonstration script documented in `docs/sop.md`.

## 20. Roadmap
- Production deployment on Kubernetes.
- External government watchlist connector via secure gRPC.
- Hardware passport scanner integration.