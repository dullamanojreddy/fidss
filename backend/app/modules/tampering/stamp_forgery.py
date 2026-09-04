"""Conservative stamp-like colour/shape candidate analysis."""

import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    image = cv2.imread(context.image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image for stamp analysis")
    if min(image.shape[:2]) < 64:
        return [], "INCONCLUSIVE", {"reason": "image_too_small"}
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    mask = cv2.inRange(hsv, (0, 70, 40), (179, 255, 240))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < max(80, image.shape[0] * image.shape[1] * 0.001):
            continue
        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        compactness = float(4 * np.pi * area / (perimeter * perimeter))
        candidates.append((area, compactness, x, y, w, h))
    metrics = {"candidate_count": len(candidates), "mean_saturation": round(float(saturation.mean()), 4)}
    if not candidates:
        return [], "SUCCESS", metrics
    area, compactness, x, y, w, h = max(candidates, key=lambda item: item[0])
    metrics.update({"largest_candidate_area": round(float(area), 2), "compactness": round(compactness, 4)})
    if len(candidates) < 2 or not (0.05 <= compactness <= 0.75):
        return [], "SUCCESS", metrics
    confidence = min(0.65, 0.25 + min(len(candidates) / 10, 0.15) + abs(compactness - 0.4) * 0.4)
    return [EvidenceItem(
        screening_id=context.screening_id, module_name="tampering", category="STAMP_IRREGULARITY_CANDIDATE", severity="LOW",
        source="tampering.stamp_forgery", confidence=round(confidence, 4),
        description="Stamp-like colour regions show shape irregularity; this is supporting evidence requiring visual review.",
        document_region=BoundingBox(x=x, y=y, width=w, height=h, label="stamp_candidate"), metrics=metrics,
    )], "SUCCESS", metrics
