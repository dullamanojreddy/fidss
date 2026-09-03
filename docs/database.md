# FIDSS Database Architecture & Schema

## 1. Design Rules
1. **UUID Primary Keys**: All entity records utilize UUIDs for safe distributed identity and non-sequential public exposure.
2. **Explicit Foreign Keys**: Cascading relationships map screenings to documents, extracted fields, module results, evidence items, reviews, and audit logs.
3. **Optimized Indexes**:
   - `screenings(screening_number, created_at, screening_level)`
   - `documents(screening_id, sha256_hash)`
   - `evidence_items(screening_id, module_name, severity)`
   - `audit_logs(screening_id, timestamp, current_hash)`
4. **Environment-Driven Configuration**:
   - In production: MySQL 8 (`DATABASE_URL=mysql+pymysql://...`)
   - In demo/development: Configurable SQLite or MySQL via environment variables.

---

## 2. Table Specifications

### `users`
- `id` (VARCHAR(36), PK)
- `username` (VARCHAR(64), UNIQUE, INDEX)
- `hashed_password` (VARCHAR(255))
- `full_name` (VARCHAR(128))
- `role` (VARCHAR(32), e.g. 'OFFICER', 'ADMIN')
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `created_at` (DATETIME)

### `screenings`
- `id` (VARCHAR(36), PK)
- `screening_number` (VARCHAR(64), UNIQUE, INDEX)
- `status` (VARCHAR(32), e.g. 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')
- `document_type` (VARCHAR(32), e.g. 'passport', 'visa', 'national_id')
- `overall_risk_score` (FLOAT, 0-100)
- `screening_level` (VARCHAR(32), 'CLEAR', 'REVIEW_RECOMMENDED', 'ENHANCED_REVIEW_RECOMMENDED', 'INCONCLUSIVE')
- `created_by` (VARCHAR(36), FK users.id)
- `created_at` (DATETIME, INDEX)
- `completed_at` (DATETIME, NULLABLE)

### `documents`
- `id` (VARCHAR(36), PK)
- `screening_id` (VARCHAR(36), FK screenings.id, INDEX)
- `original_filename` (VARCHAR(255))
- `storage_path` (VARCHAR(512))
- `file_size` (INTEGER)
- `mime_type` (VARCHAR(64))
- `sha256_hash` (VARCHAR(64), INDEX)
- `document_type` (VARCHAR(32))
- `created_at` (DATETIME)

### `document_fields`
- `id` (VARCHAR(36), PK)
- `screening_id` (VARCHAR(36), FK screenings.id, INDEX)
- `field_name` (VARCHAR(64))
- `field_value` (TEXT)
- `confidence` (FLOAT)
- `source` (VARCHAR(32), e.g. 'OCR', 'MRZ')
- `created_at` (DATETIME)

### `module_results`
- `id` (VARCHAR(36), PK)
- `screening_id` (VARCHAR(36), FK screenings.id, INDEX)
- `module_name` (VARCHAR(64))
- `status` (VARCHAR(32), 'SUCCESS', 'PARTIAL', 'FAILED', 'INCONCLUSIVE')
- `processing_time_ms` (INTEGER)
- `errors_json` (TEXT)
- `metadata_json` (TEXT)
- `created_at` (DATETIME)

### `evidence_items`
- `id` (VARCHAR(36), PK)
- `screening_id` (VARCHAR(36), FK screenings.id, INDEX)
- `module_result_id` (VARCHAR(36), FK module_results.id, NULLABLE)
- `module_name` (VARCHAR(64), INDEX)
- `category` (VARCHAR(64))
- `severity` (VARCHAR(32), 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
- `source` (VARCHAR(64))
- `confidence` (FLOAT)
- `description` (TEXT)
- `region_json` (TEXT, NULLABLE)
- `metrics_json` (TEXT, NULLABLE)
- `created_at` (DATETIME)

### `officer_reviews`
- `id` (VARCHAR(36), PK)
- `screening_id` (VARCHAR(36), FK screenings.id, UNIQUE, INDEX)
- `officer_id` (VARCHAR(36), FK users.id)
- `decision` (VARCHAR(32), 'ACCEPT', 'REJECT', 'ESCALATE', 'REQUEST_RECAPTURE', 'MARK_INCONCLUSIVE')
- `reason` (VARCHAR(64))
- `notes` (TEXT)
- `created_at` (DATETIME)

### `audit_logs`
- `id` (VARCHAR(36), PK)
- `screening_id` (VARCHAR(36), FK screenings.id, INDEX, NULLABLE)
- `previous_hash` (VARCHAR(64), NULLABLE)
- `current_hash` (VARCHAR(64), UNIQUE, INDEX)
- `event_type` (VARCHAR(64), INDEX)
- `event_payload_json` (TEXT)
- `timestamp` (DATETIME, INDEX)
- `actor_id` (VARCHAR(36), NULLABLE)

### `system_settings`
- `key` (VARCHAR(64), PK)
- `value_json` (TEXT)
- `description` (TEXT)
- `updated_by` (VARCHAR(36), NULLABLE)
- `updated_at` (DATETIME)

### `model_registry`
- `id` (VARCHAR(36), PK)
- `model_name` (VARCHAR(64), INDEX)
- `version` (VARCHAR(32))
- `runtime` (VARCHAR(32))
- `checksum` (VARCHAR(64))
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `metadata_json` (TEXT)
