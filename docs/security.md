# FIDSS Security & RBAC Architecture

## 1. Authentication & Session Management
- **Password Protection**: Passwords hashed using standard `bcrypt` with appropriate work factors.
- **JWT (JSON Web Tokens)**: Cryptographically signed access tokens using `HS256`. Expiry is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **Stateless Verification**: Every request to a protected endpoint validates token authenticity, expiry, and user active status via `get_current_user`.

## 2. Role-Based Access Control (RBAC)
- **Roles**:
  - `OFFICER`: Authorized to create screenings, review evidence, inspect audit trails, and submit officer review decisions.
  - `ADMIN`: Possesses all Officer capabilities plus updating system weights/thresholds, inspecting the model registry, and querying synthetic watchlists.
- **Enforcement**: RBAC is enforced server-side through dependency injection (`require_officer`, `require_admin`).

## 3. Upload & File Security
- **Strict Size Limits**: Files exceeding `MAX_UPLOAD_MB` (default 10MB) are rejected with HTTP 413.
- **MIME & Magic Bytes Validation**: Uploaded files are verified by inspecting magic bytes (`image/jpeg`, `image/png`).
- **Path Traversal Protection**: Uploaded files are stored with UUID filenames; user-supplied filenames are never used for disk storage.

## 4. Cryptographic Hash-Chained Audit Trail
- **Chain Formula**:
  $$\text{current\_hash} = \text{SHA256}(\text{previous\_hash} + \text{canonical\_json}(\text{payload}) + \text{timestamp})$$
- **Verification Engine**: Recursively recalculates all hash links from genesis to head. Any row alteration, payload modification, or out-of-order insert immediately raises `AUDIT_INTEGRITY_FAILURE`.
- **Blockchain Readiness**: Implements the `AuditAnchorProvider` interface allowing the local hash chain to be anchored to permissioned distributed ledgers (e.g. Hyperledger Fabric) without modifying business logic.
