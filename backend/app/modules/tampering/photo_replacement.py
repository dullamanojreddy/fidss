"""Portrait-boundary consistency check when a caller supplies a reliable region."""

import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def _portrait_box(context: DocumentContext) -> tuple[int, int, int, int] | None:
    candidate = context.allowed_outputs.get("portrait_region") if isinstance(context.allowed_outputs, dict) else None
    if not isinstance(candidate, dict):
        return None
    try:
        return tuple(int(candidate[key]) for key in ("x", "y", "width", "height"))
    except (KeyError, TypeError, ValueError):
        return None


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    box = _portrait_box(context)
    if box is None:
        return [], "INCONCLUSIVE", {"reason": "reliable_portrait_region_unavailable"}
    image = cv2.imread(context.image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image for photo analysis")
    x, y, w, h = box
    if w < 24 or h < 24 or x < 1 or y < 1 or x + w >= image.shape[1] or y + h >= image.shape[0]:
        return [], "INCONCLUSIVE", {"reason": "invalid_portrait_region"}
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    portrait = gray[y:y+h, x:x+w]
    surrounding = gray[max(0, y-h//4):min(gray.shape[0], y+h+h//4), max(0, x-w//4):min(gray.shape[1], x+w+w//4)]
    edge = cv2.Canny(gray, 80, 160)
    boundary = np.concatenate((edge[y:y+h, x], edge[y:y+h, x+w-1], edge[y, x:x+w], edge[y+h-1, x:x+w]))
    boundary_density = float(np.mean(boundary > 0))
    noise_ratio = float(np.var(portrait.astype(float) - cv2.GaussianBlur(portrait, (0, 0), 1.2)) / max(np.var(surrounding.astype(float) - cv2.GaussianBlur(surrounding, (0, 0), 1.2)), 1e-6))
    metrics = {"boundary_edge_density": round(boundary_density, 5), "noise_variance_ratio": round(noise_ratio, 5)}
    mismatch = boundary_density > 0.5 and (noise_ratio > 2.5 or noise_ratio < 0.4)
    if not mismatch:
        return [], "SUCCESS", metrics
    confidence = min(0.75, 0.35 + abs(np.log(max(noise_ratio, 1e-6))) / 3 + boundary_density / 5)
    return [EvidenceItem(
        screening_id=context.screening_id, module_name="tampering", category="PHOTO_BOUNDARY_INCONSISTENCY", severity="MEDIUM",
        source="tampering.photo_replacement", confidence=round(confidence, 4),
        description="The supplied portrait region has boundary and residual-noise discontinuities that warrant review.",
        document_region=BoundingBox(x=x, y=y, width=w, height=h, label="portrait_candidate"), metrics=metrics,
    )], "SUCCESS", metrics
