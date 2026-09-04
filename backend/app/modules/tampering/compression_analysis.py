"""Conservative JPEG recompression / ELA-style analysis."""

import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    image = cv2.imread(context.image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image for compression analysis")
    if min(image.shape[:2]) < 32:
        return [], "INCONCLUSIVE", {"reason": "image_too_small", "width": image.shape[1], "height": image.shape[0]}
    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise ValueError("JPEG recompression failed")
    recompressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    diff = cv2.absdiff(image, recompressed).mean(axis=2)
    mean_diff, max_diff = float(diff.mean()), float(diff.max())
    threshold = max(mean_diff * 4.0, 12.0)
    mask = (diff >= threshold).astype(np.uint8) * 255
    suspicious_ratio = float(np.count_nonzero(mask) / mask.size)
    metrics = {"mean_difference": round(mean_diff, 4), "max_difference": round(max_diff, 4), "threshold": round(threshold, 4), "suspicious_pixel_ratio": round(suspicious_ratio, 6), "jpeg_quality": 90}
    evidence: list[EvidenceItem] = []
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    candidates = [row for row in stats[1:count] if row[4] >= max(32, mask.size * 0.002)]
    if candidates and suspicious_ratio >= 0.002:
        x, y, w, h, area = max(candidates, key=lambda row: row[4])
        confidence = min(0.75, 0.35 + suspicious_ratio * 4 + min(max_diff / 255.0, 0.2))
        metrics.update({"candidate_count": len(candidates), "largest_region_area": int(area)})
        evidence.append(EvidenceItem(
            screening_id=context.screening_id, module_name="tampering", category="COMPRESSION_INCONSISTENCY",
            severity="MEDIUM" if suspicious_ratio >= 0.01 else "LOW", source="tampering.compression_analysis",
            confidence=round(confidence, 4), description="Localized JPEG recompression differences warrant visual review; ELA alone does not prove editing.",
            document_region=BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h), label="ela_candidate"), metrics=metrics,
        ))
    return evidence, "SUCCESS", metrics
