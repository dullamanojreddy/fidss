# P3 Sample Document Dataset

This directory is reserved for consented, legally shareable document samples used to calibrate and evaluate the tampering detectors. The repository currently contains no identity-document images.

Do not add real personal data, scraped identity documents, or synthetic images presented as genuine government documents. Before adding a sample, remove personal information, confirm redistribution rights, record its provenance, and add its SHA-256 digest and expected detector evidence to `manifest.json`.

Expected curated files are:

- `clean/passport_clean.jpg` with a matching, consented clean portrait reference
- `tampered/passport_tampered_dob.jpg`
- `tampered/passport_tampered_photo.jpg`
- `tampered/passport_tampered_stamp.jpg`
- `tampered/passport_bad_checksum.jpg`

Clean/tampered pairs should be derived from the same controlled source where possible. Expected results must describe evidence categories and acceptable metric ranges, not a bare fake/real label. Deterministic synthetic arrays used by unit tests remain in `backend/tests/unit/test_tampering.py` and are explicitly test artefacts rather than passport samples.

The empty directories and manifest are intentional until approved samples are supplied.
