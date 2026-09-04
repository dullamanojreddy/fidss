import cv2
import numpy as np

from app.modules.quality.quality_checker import analyze_quality


def create_test_image(path: str):
    """
    Create a simple document-like test image.
    """
    image = np.full((800, 1200, 3), 200, dtype=np.uint8)

    # Draw a document-like rectangle.
    cv2.rectangle(
        image,
        (100, 100),
        (1100, 700),
        (255, 255, 255),
        -1,
    )

    cv2.imwrite(path, image)


def test_quality_module_runs(tmp_path):
    image_path = tmp_path / "test_document.jpg"

    create_test_image(str(image_path))

    result = analyze_quality(str(image_path))

    assert result.status in {
        "PASS",
        "WARNING",
        "FAIL",
    }

    assert result.blur_score >= 0
    assert 0 <= result.brightness_score <= 255