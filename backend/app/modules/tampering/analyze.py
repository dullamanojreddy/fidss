"""Aggregation entry point for Person 3 tampering forensics."""

import cv2
from time import perf_counter
from app.schemas.document_context import DocumentContext
from app.schemas.module_result import ModuleResult
from . import text_manipulation, copy_move, compression_analysis, noise_analysis, photo_replacement, stamp_forgery, metadata_analysis

_DETECTORS = (
    ("text_manipulation", text_manipulation.analyze),
    ("copy_move", copy_move.analyze),
    ("compression_analysis", compression_analysis.analyze),
    ("noise_analysis", noise_analysis.analyze),
    ("photo_replacement", photo_replacement.analyze),
    ("stamp_forgery", stamp_forgery.analyze),
    ("metadata_analysis", metadata_analysis.analyze),
)


def analyze(context: DocumentContext) -> ModuleResult:
    """Run isolated detectors and return evidence, never a fake/genuine verdict."""
    started = perf_counter()
    image = cv2.imread(context.image_path)
    if image is None:
        errors = [f"{name}: unable to decode image" for name, _ in _DETECTORS]
        return ModuleResult(
            module="tampering", status="FAILED", evidence_items=[],
            processing_time_ms=int((perf_counter() - started) * 1000), errors=errors,
            metadata={"detectors": {}, "detector_statuses": {name: "FAILED" for name, _ in _DETECTORS}},
        )

    evidence = []
    errors: list[str] = []
    detector_metadata: dict[str, dict] = {}
    statuses: list[str] = []
    for name, detector in _DETECTORS:
        try:
            items, status, metadata = detector(context)
            evidence.extend(items)
            statuses.append(status)
            detector_metadata[name] = metadata
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            statuses.append("FAILED")
            detector_metadata[name] = {"error": str(exc)}
    if len(errors) == len(_DETECTORS):
        overall = "FAILED"
    elif errors:
        overall = "PARTIAL"
    elif all(status == "INCONCLUSIVE" for status in statuses):
        overall = "INCONCLUSIVE"
    else:
        overall = "SUCCESS"
    return ModuleResult(
        module="tampering", status=overall, evidence_items=evidence,
        processing_time_ms=int((perf_counter() - started) * 1000), errors=errors,
        metadata={"detectors": detector_metadata, "detector_statuses": dict(zip((name for name, _ in _DETECTORS), statuses))},
    )
