import cv2
import numpy as np


def detect_document(image: np.ndarray) -> bool:
    """
    Heuristically determine whether a document-like rectangular region
    is present in the image.

    This is a quality gate, not a document authenticity detector.
    """
    if image is None or image.size == 0:
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Reduce noise before edge detection.
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    image_area = image.shape[0] * image.shape[1]

    for contour in contours:
        area = cv2.contourArea(contour)

        # Ignore tiny regions.
        if area < image_area * 0.20:
            continue

        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0:
            continue

        approximation = cv2.approxPolyDP(
            contour,
            0.02 * perimeter,
            True,
        )

        # A document generally approximates to a quadrilateral.
        if len(approximation) == 4:
            return True

    return False