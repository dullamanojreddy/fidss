"""Local high-pass residual-noise comparison."""

import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    image = cv2.imread(context.image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Unable to decode image for noise analysis")
    height, width = image.shape
    if min(height, width) < 64:
        return [], "INCONCLUSIVE", {"reason": "image_too_small", "width": width, "height": height}
    residual = image.astype(np.float32) - cv2.GaussianBlur(image, (0, 0), 1.2).astype(np.float32)
    baseline = float(np.var(residual))
    grid = 4
    regions: list[tuple[float, int, int, int, int]] = []
    for row in range(grid):
        for col in range(grid):
            y0, y1 = row * height // grid, (row + 1) * height // grid
            x0, x1 = col * width // grid, (col + 1) * width // grid
            variance = float(np.var(residual[y0:y1, x0:x1]))
            deviation = abs(variance - baseline) / max(baseline, 1e-6)
            regions.append((deviation, x0, y0, x1 - x0, y1 - y0))
    strongest = max(regions, default=(0.0, 0, 0, 0, 0))
    metrics = {"baseline_residual_variance": round(baseline, 5), "max_normalized_deviation": round(strongest[0], 5), "grid_regions": len(regions)}
    if baseline < 0.01:
        return [], "INCONCLUSIVE", {**metrics, "reason": "insufficient_noise_signal"}
    if strongest[0] >= 1.5:
        deviation, x, y, w, h = strongest
        confidence = min(0.7, 0.3 + deviation / 5)
        return [EvidenceItem(
            screening_id=context.screening_id, module_name="tampering", category="NOISE_INCONSISTENCY", severity="LOW" if deviation < 2.5 else "MEDIUM",
            source="tampering.noise_analysis", confidence=round(confidence, 4),
            description="A local residual-noise level differs from the document-wide baseline and warrants review.",
            document_region=BoundingBox(x=x, y=y, width=w, height=h, label="noise_candidate"), metrics=metrics,
        )], "SUCCESS", metrics
    return [], "SUCCESS", metrics
