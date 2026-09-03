# FIDSS Architecture Specification

## 1. System Architecture Diagram

```text
                                +---------------------------+
                                |  React 18 + Vite Frontend |
                                |  (TailwindCSS + Lucide)   |
                                +-------------+-------------+
                                              | REST + JWT
                                +-------------v-------------+
                                |      FastAPI Backend      |
                                | (Auth, RBAC, REST Routes) |
                                +-------------+-------------+
                                              |
                                +-------------v-------------+
                                |   Screening Orchestrator  |
                                |    (12-Step Pipeline)     |
                                +-------------+-------------+
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
         +-----------v-----------++-----------v-----------++-----------v-----------+
         | P1 OCR & Preprocessing|| P2 Validation & Rules || P3 Forensics / CV     |
         +-----------+-----------++-----------+-----------++-----------+-----------+
                     |                        |                        |
                     +------------------------+------------------------+
                                              |
                                 +------------v------------+
                                 |   P4 Face Verification  |
                                 +------------+------------+
                                              |
                                 +------------v------------+
                                 |    P4 Evidence Fusion   |
                                 +------------+------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
         +-----------v-----------+                         +-----------v-----------+
         |  Database Persistence |                         |  SHA-256 Audit Chain  |
         | (SQLAlchemy / MySQL)  |                         |  (Tamper-Evident Log) |
         +-----------------------+                         +-----------------------+
```

## 2. Orchestrator 12-Step Execution Flow
1. **01_RECEIVE_UPLOAD**: Accept multipart document image and optional selfie image from authenticated officer.
2. **02_VALIDATE_FILE**: Validate MIME magic bytes, extension, and file size limits (<= 10MB).
3. **03_COMPUTE_SHA256**: Calculate cryptographic document hash for deduplication and audit tracking.
4. **04_STORE_DOCUMENT**: Securely store file in partitioned storage using UUID naming to prevent path traversal.
5. **05_DETERMINE_DOC_TYPE**: Identify document class (`passport`, `visa`, `national_id`, `driving_license`).
6. **06_IMAGE_QUALITY_CHECK**: Execute P1 Quality gate (blur, resolution, brightness, orientation, presence). If `FAIL`, halt with `INCONCLUSIVE` / recapture recommendation.
7. **07_OCR_EXTRACTION**: Execute P1 OCR pipeline to extract text tokens, bounding boxes, and normalize semantic fields.
8. **08_VALIDATION_MRZ**: Execute P2 MRZ parser, 7-3-1 check digit validator, cross-validation against OCR, and synthetic watchlist query.
9. **09_TAMPERING_FORENSICS**: Execute P3 forensic checks (copy-move, ELA compression, noise variance, text baseline, stamp integrity).
10. **10_FACE_VERIFICATION**: Execute P4 face detection (SCRFD) and embedding match (ArcFace) against selfie (if provided).
11. **11_FUSION_RISK_AGGREGATION**: Execute P4 evidence fusion to calculate 0-100 risk score and assign screening level (`CLEAR`, `REVIEW_RECOMMENDED`, `ENHANCED_REVIEW_RECOMMENDED`, `INCONCLUSIVE`).
12. **12_PERSISTENCE_AUDIT_LOG**: Write normalized screening records, module results, and evidence items to database; append `SCREENING_CREATED` event to SHA-256 audit chain.

## 3. Module Dispatcher Pattern
To enforce strict boundary isolation between Person 5 and Persons 1–4, the orchestrator communicates through `ModuleDispatcher`. The dispatcher loads the real analytical module when present or falls back to a verified contract-conforming stub, logging all execution times and errors cleanly without crashing the platform.
