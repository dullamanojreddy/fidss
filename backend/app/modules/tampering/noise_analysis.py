"""Local high-pass residual-noise comparison."""

import cv2
import numpy as np
import pywt
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
    gaussian_baseline = float(np.var(residual))
    approximation, details = pywt.dwt2(image.astype(np.float32), "haar")
    wavelet_residual = pywt.idwt2((np.zeros_like(approximation), details), "haar")[:height, :width]
    wavelet_baseline = float(np.var(wavelet_residual))
    grid = 4
    regions: list[tuple[float, float, float, int, int, int, int]] = []
    for row in range(grid):
        for col in range(grid):
            y0, y1 = row * height // grid, (row + 1) * height // grid
            x0, x1 = col * width // grid, (col + 1) * width // grid
            gaussian_variance = float(np.var(residual[y0:y1, x0:x1]))
            wavelet_variance = float(np.var(wavelet_residual[y0:y1, x0:x1]))
            gaussian_deviation = abs(gaussian_variance - gaussian_baseline) / max(gaussian_baseline, 1e-6)
            wavelet_deviation = abs(wavelet_variance - wavelet_baseline) / max(wavelet_baseline, 1e-6)
            combined_deviation = (gaussian_deviation + wavelet_deviation) / 2.0
            regions.append((combined_deviation, gaussian_deviation, wavelet_deviation, x0, y0, x1 - x0, y1 - y0))
    strongest = max(regions, default=(0.0, 0.0, 0.0, 0, 0, 0, 0))
    metrics = {
        "gaussian_residual_variance": round(gaussian_baseline, 5),
        "wavelet_residual_variance": round(wavelet_baseline, 5),
        "max_gaussian_deviation": round(strongest[1], 5),
        "max_wavelet_deviation": round(strongest[2], 5),
        "max_combined_deviation": round(strongest[0], 5),
        "wavelet": "haar", "grid_regions": len(regions),
    }
    if gaussian_baseline < 0.01 and wavelet_baseline < 0.01:
        return [], "INCONCLUSIVE", {**metrics, "reason": "insufficient_noise_signal"}
    if strongest[0] >= 1.5:
        deviation, _, _, x, y, w, h = strongest
        confidence = min(0.7, 0.3 + deviation / 5)
        return [EvidenceItem(
            screening_id=context.screening_id, module_name="tampering", category="NOISE_INCONSISTENCY", severity="LOW" if deviation < 2.5 else "MEDIUM",
            source="tampering.noise_analysis", confidence=round(confidence, 4),
            description="A local residual-noise level differs from the document-wide baseline and warrants review.",
            document_region=BoundingBox(x=x, y=y, width=w, height=h, label="noise_candidate"), metrics=metrics,
        )], "SUCCESS", metrics
    return [], "SUCCESS", metrics
