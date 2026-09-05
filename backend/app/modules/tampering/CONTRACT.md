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
- Combined Gaussian high-pass and Haar-wavelet residual-noise inconsistency
- Portrait-boundary consistency, when an explicit portrait region is supplied
- Stamp-like colour/shape candidate irregularity
- Image metadata and editing-software indicators

## Evidence and failure rules
- No fake/real verdict or fraud probability is produced.
- A single detector is supporting evidence, never proof.
- Missing EXIF and missing OCR/layout data are normal conditions.
- Missing upstream evidence does not equal tampering.
- Individual detector failures are captured; other detectors continue. A corrupt image produces `FAILED`; insufficient usable signals produce `INCONCLUSIVE`; partial detector failure produces `PARTIAL`.

Detector status semantics are: `SUCCESS` when a detector completed with meaningful measurements (with or without evidence), `INCONCLUSIVE` when required evidence is unavailable or insufficient, and `FAILED` on an execution failure. The aggregate is `FAILED` when every detector fails, `PARTIAL` when only some fail, `INCONCLUSIVE` when all completed detectors are inconclusive, and otherwise `SUCCESS`.

## Dependencies
Pillow, NumPy, OpenCV, and PyWavelets. The module is CPU-only.

## Limitations
P1 supplies OCR geometry in `DocumentContext.ocr_result["raw_lines"]`. Each line contains `text`, a numeric `confidence`, and a four-corner PaddleOCR polygon under `bbox`: `[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]`. P3 converts finite polygon coordinates to an enclosing rectangle, validates that rectangle against the decoded image dimensions, rejects boxes covering more than half the image, and removes only near-identical overlaps (IoU at least 0.9). Missing, malformed, out-of-image, oversized, duplicate, or fewer than four valid lines cannot establish tampering and produce `INCONCLUSIVE` when insufficient geometry remains.

P1 generates coordinates after resize, optional perspective correction, and deskew, but currently does not publish processed-image dimensions or a transform back to the source image. Geometry aligns directly only when preprocessing leaves the coordinate plane unchanged. P3 cannot safely correct that upstream ambiguity; P1/P5 must eventually provide processed dimensions and a source-coordinate transform. Portrait regions are also optional. P3 never invents regions, and all findings remain review candidates rather than fraud verdicts. Heuristic thresholds require calibration against curated document samples before deployment.

## Test command
From `backend`: `python -m pytest tests/unit/test_tampering.py -q`

## Handoff and boundaries
Person 5 can call the existing dispatcher unchanged; it imports `app.modules.tampering.analyze` and invokes `analyze(context)`. This package does not change OCR, validation, face verification, fusion, schemas, persistence, orchestration, APIs, or frontend code.
