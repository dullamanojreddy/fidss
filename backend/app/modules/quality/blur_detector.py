import cv2
import numpy as np


def calculate_blur_score(image: np.ndarray) -> float:
    """
    Calculate image sharpness using Laplacian variance.

    Higher score = sharper image.
    Lower score = blurrier image.

    Returns:
        float: Laplacian variance.
    """
    if image is None or image.size == 0:
        return 0.0

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    return float(cv2.Laplacian(gray, cv2.CV_64F).var())