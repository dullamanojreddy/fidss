import numpy as np


# Minimum dimensions needed for useful OCR.
MIN_WIDTH = 600
MIN_HEIGHT = 400


def check_resolution(image: np.ndarray) -> bool:
    """
    Check whether the image has sufficient resolution for OCR.

    Returns:
        bool: True if resolution is acceptable.
    """
    if image is None or image.size == 0:
        return False

    height, width = image.shape[:2]

    return width >= MIN_WIDTH and height >= MIN_HEIGHT