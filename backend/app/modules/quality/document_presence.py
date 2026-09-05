import cv2
import numpy as np


def detect_document(image: np.ndarray) -> bool:
    if image is None or image.size == 0:
        return False

    height, width = image.shape[:2]
    image_area = height * width

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # ---------------------------------------------------------
    # Method 1: Look for a large rectangular document contour
    # ---------------------------------------------------------
    for low, high in [(30, 100), (50, 150), (75, 200)]:
        edges = cv2.Canny(blurred, low, high)

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (7, 7),
        )

        closed = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            kernel,
        )

        contours, _ = cv2.findContours(
            closed,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < image_area * 0.15:
                continue

            perimeter = cv2.arcLength(contour, True)

            if perimeter == 0:
                continue

            approximation = cv2.approxPolyDP(
                contour,
                0.04 * perimeter,
                True,
            )

            if len(approximation) == 4:
                return True

    # ---------------------------------------------------------
    # Method 2: Check for meaningful structure in the image
    #
    # Useful when the document border isn't detected as one
    # clean contour.
    # ---------------------------------------------------------
    edges = cv2.Canny(blurred, 50, 150)

    # Ignore a small margin around the image.
    margin_y = int(height * 0.05)
    margin_x = int(width * 0.05)

    central_edges = edges[
        margin_y:height - margin_y,
        margin_x:width - margin_x,
    ]

    edge_density = np.count_nonzero(central_edges) / central_edges.size

    # A document image normally contains substantial text,
    # MRZ lines, portrait boundaries, printed fields, etc.
    if edge_density >= 0.02:
        return True

    return False