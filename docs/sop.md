# FIDSS Standard Operating Procedure & Demonstration Script

## 1. Demo Walkthrough Script
1. **Login**: Authenticate as `Inspector Arjun` (Role: Officer).
2. **Dashboard**: Observe real-time checkpoint statistics: screening volume, risk distributions, and module health.
3. **Screening Console**:
   - Inspect active screening ID and document preview (Passport of Republic of India).
   - Review 7-step pipeline status (Upload -> OCR -> MRZ -> Tampering -> Face -> Risk -> Completed).
   - Inspect Risk Score badge (18 / 100, CLEAR), Extracted Document Information grid, and Key Findings.
   - Review individual Module Results cards.
4. **Officer Review**:
   - Click "Proceed to Review".
   - Review evidence findings and select decision `ACCEPT`. Add rationale note and submit.
5. **Audit Trail & Verification**:
   - Navigate to Audit Trail. View hash-chained blocks with timestamps and SHA-256 links.
   - Click "Verify Audit Integrity" -> Observe Green verification pass.
   - Click "Simulate Audit Tampering" -> Observe immediate Red `AUDIT_INTEGRITY_FAILURE`, proving cryptographic defense.

## 2. Real vs Synthetic Framing
- **Real**: OCR extraction, MRZ checksum calculations, face verification, forensic tampering detection, and SHA-256 hash chains.
- **Synthetic**: Watchlist data is prototype demonstration data.
- **Blockchain-Ready**: Uses local hash chain with pluggable `AuditAnchorProvider` ready for distributed ledger anchoring.
