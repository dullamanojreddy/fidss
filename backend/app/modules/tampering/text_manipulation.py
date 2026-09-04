"""OCR-layout text geometry and local appearance checks."""

import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def _tokens(ocr_result: dict | None) -> list[dict]:
    if not isinstance(ocr_result, dict):
        return []
    for key in ("tokens", "text_boxes", "bounding_boxes", "boxes"):
        value = ocr_result.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _box(token: dict) -> tuple[int, int, int, int] | None:
    candidate = token.get("bounding_box") or token.get("bbox") or token
    try:
        if all(key in candidate for key in ("x", "y", "width", "height")):
            return tuple(int(candidate[key]) for key in ("x", "y", "width", "height"))
    except (TypeError, ValueError):
        pass
    return None


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    tokens = [(token, _box(token)) for token in _tokens(context.ocr_result)]
    tokens = [(token, box) for token, box in tokens if box and box[2] > 0 and box[3] > 0]
    if len(tokens) < 4:
        return [], "INCONCLUSIVE", {"reason": "stable_ocr_boxes_unavailable", "token_count": len(tokens)}
    image = cv2.imread(context.image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image for text analysis")
    heights = np.array([box[3] for _, box in tokens], dtype=float)
    median_height = float(np.median(heights))
    deviations = np.abs(heights - median_height) / max(median_height, 1.0)
    idx = int(np.argmax(deviations))
    token, (x, y, w, h) = tokens[idx]
    patch = image[max(0, y):min(image.shape[0], y + h), max(0, x):min(image.shape[1], x + w)]
    surrounding = image[max(0, y - h):min(image.shape[0], y + 2 * h), max(0, x - w):min(image.shape[1], x + 2 * w)]
    color_difference = float(abs(patch.mean() - surrounding.mean())) if patch.size and surrounding.size else 0.0
    metrics = {"token_count": len(tokens), "median_height": round(median_height, 4), "height_deviation": round(float(deviations[idx]), 4), "color_difference": round(color_difference, 4)}
    if deviations[idx] < 0.45 and color_difference < 25:
        return [], "SUCCESS", metrics
    confidence = min(0.7, 0.25 + float(deviations[idx]) * 0.35 + min(color_difference / 150, 0.2))
    return [EvidenceItem(
        screening_id=context.screening_id, module_name="tampering", category="TEXT_MANIPULATION_CANDIDATE",
        severity="LOW" if confidence < 0.5 else "MEDIUM", source="tampering.text_manipulation", confidence=round(confidence, 4),
        description="Local text geometry or appearance is inconsistent with supplied OCR layout; manual review is required.",
        document_region=BoundingBox(x=x, y=y, width=w, height=h, label="ocr_text_candidate"), metrics=metrics,
    )], "SUCCESS", metrics
