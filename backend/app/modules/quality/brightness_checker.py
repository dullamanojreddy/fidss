import cv2
import numpy as np


def calculate_brightness_score(image: np.ndarray) -> float:
    """
    Calculate mean image brightness.

    Returns:
        float: Mean grayscale intensity from 0 to 255.
    """
    if image is None or image.size == 0:
        return 0.0

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    return float(np.mean(gray))


def check_brightness(
    brightness_score: float,
    min_brightness: float = 40.0,
    max_brightness: float = 220.0,
) -> bool:
    """
    Check whether image brightness is within a usable range.
    """
    return min_brightness <= brightness_score <= max_brightness