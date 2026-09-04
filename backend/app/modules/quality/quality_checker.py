import cv2
import numpy as np

from app.schemas.quality_result import QualityResult

from .blur_detector import calculate_blur_score
from .resolution_checker import check_resolution
from .brightness_checker import (
    calculate_brightness_score,
    check_brightness,
)
from .orientation_checker import get_orientation
from .document_presence import detect_document


# Initial quality thresholds.
# These should eventually be configurable.
MIN_BLUR_SCORE = 50.0


def analyze_quality(image_path: str) -> QualityResult:
    """
    Run all image quality checks and return a QualityResult.
    """

    issues: list[str] = []

    # ---------------------------------------------------------
    # Load image
    # ---------------------------------------------------------

    image = cv2.imread(image_path)

    if image is None:
        return QualityResult(
            status="FAIL",
            blur_score=0.0,
            brightness_score=0.0,
            resolution_ok=False,
            document_detected=False,
            orientation="0_DEG",
            quality_issues=["Unable to decode image"],
        )

    # ---------------------------------------------------------
    # Blur
    # ---------------------------------------------------------

    blur_score = calculate_blur_score(image)

    if blur_score < MIN_BLUR_SCORE:
        issues.append(
            f"Image is too blurry (blur score: {blur_score:.2f})"
        )

    # ---------------------------------------------------------
    # Resolution
    # ---------------------------------------------------------

    resolution_ok = check_resolution(image)

    if not resolution_ok:
        height, width = image.shape[:2]

        issues.append(
            f"Image resolution is too low ({width}x{height})"
        )

    # ---------------------------------------------------------
    # Brightness
    # ---------------------------------------------------------

    brightness_score = calculate_brightness_score(image)

    brightness_ok = check_brightness(brightness_score)

    if not brightness_ok:
        issues.append(
            f"Image brightness is outside usable range "
            f"({brightness_score:.2f})"
        )

    # ---------------------------------------------------------
    # Document presence
    # ---------------------------------------------------------

    document_detected = detect_document(image)

    if not document_detected:
        issues.append("No document-like region detected")

    # ---------------------------------------------------------
    # Orientation
    # ---------------------------------------------------------

    orientation = get_orientation(image_path)

    if orientation != "0_DEG":
        issues.append(
            f"Image EXIF orientation indicates {orientation}"
        )

    # ---------------------------------------------------------
    # Determine overall status
    # ---------------------------------------------------------

    critical_failure = (
        not resolution_ok
        or not document_detected
    )

    quality_warning = (
        blur_score < MIN_BLUR_SCORE
        or not brightness_ok
        or orientation != "0_DEG"
    )

    if critical_failure:
        status = "FAIL"
    elif quality_warning:
        status = "WARNING"
    else:
        status = "PASS"

    return QualityResult(
        status=status,
        blur_score=blur_score,
        brightness_score=brightness_score,
        resolution_ok=resolution_ok,
        document_detected=document_detected,
        orientation=orientation,
        quality_issues=issues,
    )