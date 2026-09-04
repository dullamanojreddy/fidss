# Tampering Module Contract

## Owner
Person 3 — Vallu

## Purpose
Generate layered, classical-computer-vision forensic evidence from an identity-document image. This module does not determine whether a document is fake or genuine.

## Input and output
`analyze(context: DocumentContext) -> ModuleResult`

The module reuses `DocumentContext`, `ModuleResult`, `EvidenceItem`, and `BoundingBox` from `app.schemas`. Evidence has the repository-required screening ID, module name, category, severity, source, calculated confidence, description, optional region, and metrics.

## Detectors
- Text geometry and local appearance
- ORB copy-move matching with ratio test and RANSAC
- JPEG recompression / ELA-style inconsistency
- Local residual-noise inconsistency
- Portrait-boundary consistency, when an explicit portrait region is supplied
- Stamp-like colour/shape candidate irregularity
- Image metadata and editing-software indicators

## Evidence and failure rules
- No fake/real verdict or fraud probability is produced.
- A single detector is supporting evidence, never proof.
- Missing EXIF and missing OCR/layout data are normal conditions.
- Individual detector failures are captured; other detectors continue. A corrupt image produces `FAILED`; insufficient usable signals produce `INCONCLUSIVE`; partial detector failure produces `PARTIAL`.

## Dependencies
Pillow, NumPy, and OpenCV. The module is CPU-only.

## Limitations
OCR bounding boxes and portrait regions are optional and not standardized by the shared contract. The text and photo detectors do not invent them. Heuristic thresholds are conservative demo defaults and require calibration against curated document samples before deployment.

## Test command
From `backend`: `python -m pytest app/modules/tampering/test_tampering.py -q`

## Handoff and boundaries
Person 5 can call the existing dispatcher unchanged; it imports `app.modules.tampering.analyze` and invokes `analyze(context)`. This package does not change OCR, validation, face verification, fusion, schemas, persistence, orchestration, APIs, or frontend code.
