from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def load_image(image_path: str) -> np.ndarray:
    """
    Safely load an image from disk.

    Returns:
        OpenCV BGR image.

    Raises:
        FileNotFoundError: if the image does not exist.
        ValueError: if the image cannot be decoded.
    """
    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # PIL handles EXIF orientation correctly when exif_transpose is used.
    try:
        with Image.open(path) as pil_image:
            pil_image = ImageOps.exif_transpose(pil_image)
            pil_image = pil_image.convert("RGB")

            image = np.array(pil_image)

    except Exception as exc:
        raise ValueError(f"Unable to decode image: {image_path}") from exc

    # Convert RGB → BGR for OpenCV.
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def resize_for_processing(
    image: np.ndarray,
    max_dimension: int = 2000,
) -> np.ndarray:
    """
    Resize an image while preserving its aspect ratio.

    Images smaller than max_dimension are left unchanged.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image")

    height, width = image.shape[:2]
    largest_dimension = max(height, width)

    if largest_dimension <= max_dimension:
        return image.copy()

    scale = max_dimension / largest_dimension

    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA,
    )


def find_document_contour(image: np.ndarray) -> np.ndarray | None:
    """
    Try to find the largest quadrilateral representing a document.

    Returns:
        Four-point contour or None if no suitable document is found.
    """
    if image is None or image.size == 0:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Reduce small noise before detecting edges.
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    image_area = image.shape[0] * image.shape[1]

    # Largest contours first.
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

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

        if len(approximation) == 4:
            return approximation.reshape(4, 2).astype(np.float32)

    return None


def order_points(points: np.ndarray) -> np.ndarray:
    """
    Order four points as:

        top-left
        top-right
        bottom-right
        bottom-left
    """
    points = np.asarray(points, dtype=np.float32)

    if points.shape != (4, 2):
        raise ValueError("Expected exactly four points")

    ordered = np.zeros((4, 2), dtype=np.float32)

    sums = points.sum(axis=1)
    differences = np.diff(points, axis=1).reshape(-1)

    ordered[0] = points[np.argmin(sums)]          # top-left
    ordered[2] = points[np.argmax(sums)]          # bottom-right
    ordered[1] = points[np.argmin(differences)]  # top-right
    ordered[3] = points[np.argmax(differences)]  # bottom-left

    return ordered


def perspective_correct(
    image: np.ndarray,
    points: np.ndarray,
) -> np.ndarray:
    """
    Apply a four-point perspective transformation.
    """
    rect = order_points(points)

    top_left, top_right, bottom_right, bottom_left = rect

    width_top = np.linalg.norm(top_right - top_left)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)

    height_left = np.linalg.norm(bottom_left - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)

    width = max(int(width_top), int(width_bottom))
    height = max(int(height_left), int(height_right))

    if width <= 0 or height <= 0:
        raise ValueError("Invalid document dimensions")

    destination = np.array(
        [
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1],
        ],
        dtype=np.float32,
    )

    matrix = cv2.getPerspectiveTransform(rect, destination)

    return cv2.warpPerspective(
        image,
        matrix,
        (width, height),
    )


def deskew(image: np.ndarray) -> np.ndarray:
    """
    Correct small text/document rotation.

    Uses the dominant angle of foreground pixels.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Binary image: dark document/text regions become foreground.
    _, threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    coordinates = np.column_stack(np.where(threshold > 0))

    # Not enough information to estimate an angle.
    if len(coordinates) < 100:
        return image.copy()

    angle = cv2.minAreaRect(coordinates)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Ignore extremely large rotations here.
    # Those should be handled by orientation correction.
    if abs(angle) < 0.1 or abs(angle) > 15:
        return image.copy()

    height, width = image.shape[:2]
    center = (width // 2, height // 2)

    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0,
    )

    return cv2.warpAffine(
        image,
        rotation_matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def preprocess_image(
    image_path: str,
    max_dimension: int = 2000,
) -> np.ndarray:
    """
    Complete preprocessing pipeline for OCR.

    Steps:
        1. Load and correct EXIF orientation.
        2. Resize very large images.
        3. Detect the document boundary.
        4. Correct perspective when possible.
        5. Deskew the result.

    If a document contour cannot be found, the original resized
    image is returned rather than failing the entire OCR pipeline.
    """
    image = load_image(image_path)

    image = resize_for_processing(
        image,
        max_dimension=max_dimension,
    )

    document_contour = find_document_contour(image)

    if document_contour is not None:
        image = perspective_correct(
            image,
            document_contour,
        )

    image = deskew(image)

    return image