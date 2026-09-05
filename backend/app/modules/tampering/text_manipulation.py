"""OCR-layout text geometry and local appearance checks."""

import math
import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def _tokens(ocr_result: dict | None) -> list[dict]:
    if not isinstance(ocr_result, dict):
        return []
    for key in ("raw_lines", "tokens", "text_boxes", "bounding_boxes", "boxes"):
        value = ocr_result.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _box(token: dict) -> tuple[int, int, int, int] | None:
    candidate = token.get("bounding_box") or token.get("bbox") or token
    if isinstance(candidate, (list, tuple)):
        try:
            if len(candidate) != 4 or any(len(point) != 2 for point in candidate):
                return None
            xs = [float(point[0]) for point in candidate]
            ys = [float(point[1]) for point in candidate]
            if not all(math.isfinite(value) for value in (*xs, *ys)):
                return None
            x_min, y_min = math.floor(min(xs)), math.floor(min(ys))
            x_max, y_max = math.ceil(max(xs)), math.ceil(max(ys))
            return x_min, y_min, x_max - x_min, y_max - y_min
        except (TypeError, ValueError, OverflowError):
            return None
    if not isinstance(candidate, dict):
        return None
    try:
        if all(key in candidate for key in ("x", "y", "width", "height")):
            values = tuple(float(candidate[key]) for key in ("x", "y", "width", "height"))
            if all(math.isfinite(value) and value.is_integer() for value in values):
                return tuple(int(value) for value in values)
    except (TypeError, ValueError, OverflowError):
        pass
    return None


def _intersection_over_union(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    intersection_width = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    intersection_height = max(0, min(ay + ah, by + bh) - max(ay, by))
    intersection = intersection_width * intersection_height
    union = aw * ah + bw * bh - intersection
    return intersection / union if union else 0.0


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    supplied_tokens = _tokens(context.ocr_result)
    if not supplied_tokens:
        return [], "INCONCLUSIVE", {
            "reason": "stable_ocr_boxes_unavailable", "supplied_token_count": 0, "valid_token_count": 0,
        }
    image = cv2.imread(context.image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image for text analysis")
    image_height, image_width = image.shape[:2]
    image_area = image_width * image_height
    tokens: list[tuple[dict, tuple[int, int, int, int]]] = []
    malformed_count = out_of_image_count = oversized_count = duplicate_overlap_count = 0
    for token in supplied_tokens:
        box = _box(token)
        if box is None or box[2] <= 0 or box[3] <= 0:
            malformed_count += 1
            continue
        x, y, width, height = box
        if x < 0 or y < 0 or x + width > image_width or y + height > image_height:
            out_of_image_count += 1
            continue
        if width * height > image_area * 0.5:
            oversized_count += 1
            continue
        if any(_intersection_over_union(box, accepted_box) >= 0.9 for _, accepted_box in tokens):
            duplicate_overlap_count += 1
            continue
        tokens.append((token, box))
    validation_metrics = {
        "supplied_token_count": len(supplied_tokens), "valid_token_count": len(tokens),
        "invalid_token_count": len(supplied_tokens) - len(tokens), "malformed_box_count": malformed_count,
        "out_of_image_box_count": out_of_image_count, "oversized_box_count": oversized_count,
        "duplicate_overlap_box_count": duplicate_overlap_count, "image_width": image_width,
        "image_height": image_height, "coordinate_system": "original_image_pixels_exif_oriented",
    }
    if len(tokens) < 4:
        return [], "INCONCLUSIVE", {**validation_metrics, "reason": "insufficient_valid_ocr_boxes"}
    heights = np.array([box[3] for _, box in tokens], dtype=float)
    median_height = float(np.median(heights))
    deviations = np.abs(heights - median_height) / max(median_height, 1.0)
    idx = int(np.argmax(deviations))
    token, (x, y, w, h) = tokens[idx]
    patch = image[max(0, y):min(image.shape[0], y + h), max(0, x):min(image.shape[1], x + w)]
    surrounding = image[max(0, y - h):min(image.shape[0], y + 2 * h), max(0, x - w):min(image.shape[1], x + 2 * w)]
    color_difference = float(abs(patch.mean() - surrounding.mean())) if patch.size and surrounding.size else 0.0
    confidences = [float(token["confidence"]) for token, _ in tokens if isinstance(token.get("confidence"), (int, float)) and math.isfinite(float(token["confidence"]))]
    metrics = {
        **validation_metrics, "mean_ocr_confidence": round(float(np.mean(confidences)), 5) if confidences else "unavailable",
        "median_height": round(median_height, 4), "height_deviation": round(float(deviations[idx]), 4),
        "color_difference": round(color_difference, 4),
    }
    # Different font sizes are normal document layout. Require an appearance
    # discontinuity as well as a strong geometry outlier before raising evidence.
    if deviations[idx] < 0.75 or color_difference < 25:
        return [], "SUCCESS", metrics
    confidence = min(0.7, 0.25 + float(deviations[idx]) * 0.35 + min(color_difference / 150, 0.2))
    return [EvidenceItem(
        screening_id=context.screening_id, module_name="tampering", category="TEXT_MANIPULATION_CANDIDATE",
        severity="LOW" if confidence < 0.5 else "MEDIUM", source="tampering.text_manipulation", confidence=round(confidence, 4),
        description="Local text geometry or appearance is inconsistent with supplied OCR layout; manual review is required.",
        document_region=BoundingBox(x=x, y=y, width=w, height=h, label="ocr_text_candidate"), metrics=metrics,
    )], "SUCCESS", metrics
