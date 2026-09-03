# FIDSS API Contracts

All endpoints return JSON responses and use standard HTTP status codes. Secured endpoints require header `Authorization: Bearer <token>`.

## 1. Authentication Endpoints

### `POST /api/auth/login`
- **Request (JSON or Form)**:
  ```json
  { "username": "arjun", "password": "secure_password" }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "c1f72a44-...",
      "username": "arjun",
      "full_name": "Inspector Arjun",
      "role": "OFFICER"
    }
  }
  ```

### `GET /api/auth/me`
- **Response (200 OK)**: Authenticated user object.

---

## 2. Screening Endpoints

### `POST /api/screenings`
- **Request (Multipart Form Data)**:
  - `document`: File (Required, image/jpeg, image/png)
  - `selfie`: File (Optional)
  - `document_type`: string (Optional, default: `passport`)
- **Response (201 Created)**: Full `ScreeningResultResponse` object.

### `GET /api/screenings`
- **Query Params**: `page=1`, `limit=20`, `level=CLEAR|REVIEW_RECOMMENDED`, `search=...`
- **Response (200 OK)**: Paginated list of screening summaries.

### `GET /api/screenings/{id}`
- **Response (200 OK)**: Detailed screening object including metadata, document info, risk score, module results, and extracted fields.

### `GET /api/screenings/{id}/evidence`
- **Response (200 OK)**: Array of `EvidenceItem` objects with provenance fields (`module_name`, `module_result_id`).

---

## 3. Documents & Reviews

### `GET /api/documents/{id}/file`
- **Response (200 OK)**: Streams the document image file with cache headers.

### `POST /api/screenings/{id}/review`
- **Request (JSON)**:
  ```json
  {
    "decision": "ACCEPT",
    "reason": "VERIFIED_VALID",
    "notes": "Visual check confirmed all fields correspond to valid traveler."
  }
  ```
- **Response (200 OK)**: Created review record with timestamp and linked audit event.

---

## 4. Audit & Verification

### `GET /api/audit/logs`
- **Response (200 OK)**: Chronological list of hash-chained audit blocks.

### `POST /api/audit/{screening_id}/verify`
- **Response (200 OK)**:
  ```json
  {
    "screening_id": "...",
    "status": "VERIFIED",
    "total_events": 5,
    "chain_valid": true,
    "message": "All cryptographic hashes match unbroken chain."
  }
  ```

### `POST /api/audit/tamper-demo`
- **Request (JSON)**: `{ "screening_id": "..." }`
- **Response (200 OK)**: Simulates tampering on a database row to demonstrate that `/verify` detects the discrepancy and returns `AUDIT_INTEGRITY_FAILURE`.

---

## 5. Dashboard & Settings

### `GET /api/dashboard`
- **Response (200 OK)**: System statistics: total screenings, clear count, review recommended count, inconclusive count, average latency, and recent activity.

### `GET /api/settings`
- **Response (200 OK)**: Read-only access to system thresholds (face similarity threshold, quality tolerance, module weights).

### `PUT /api/settings` (Admin Only)
- **Request (JSON)**: Dictionary of updated key/value pairs. Logs `SYSTEM_SETTING_CHANGED` into audit chain.
