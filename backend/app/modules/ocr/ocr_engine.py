from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from paddleocr import PaddleOCR


@dataclass
class OCRLine:
    """One piece of text detected by OCR."""

    text: str
    confidence: float
    bbox: list[list[float]]


class OCREngine:
    """
    Wrapper around PaddleOCR.

    The engine is created once and reused so that the OCR model
    does not need to be loaded for every document.
    """

    def __init__(self) -> None:
        self._ocr = PaddleOCR(
            lang="en",
            use_gpu=False,
            show_log=False,
            use_angle_cls=False,
        )

    def recognize(self, image: np.ndarray) -> list[OCRLine]:
        """
        Run OCR on an OpenCV image.

        Returns:
            A list of detected text lines with confidence and
            bounding-box information.
        """
        if image is None or image.size == 0:
            return []

        result = self._ocr.ocr(image, cls=False)
        if not result or not result[0]:
            return []

        lines: list[OCRLine] = []

        for item in result[0]:
            if not item or len(item) < 2:
                continue

            box = item[0]
            text_score = item[1]
            if isinstance(text_score, (tuple, list)) and len(text_score) >= 2:
                text = str(text_score[0]).strip()
                score = float(text_score[1])
            else:
                text = str(text_score).strip()
                score = 0.90

            if not text:
                continue

            lines.append(
                OCRLine(
                    text=text,
                    confidence=score,
                    bbox=np.asarray(box).tolist(),
                )
            )

        return lines


_engine: OCREngine | None = None


def get_ocr_engine() -> OCREngine:
    """
    Get the shared OCR engine instance.

    Loading an OCR model is expensive, so we reuse one instance
    instead of loading the model for every document.
    """
    global _engine

    if _engine is None:
        _engine = OCREngine()

    return _engine


def run_ocr(image: np.ndarray) -> list[OCRLine]:
    """Convenience function used by the FIDSS OCR module."""
    return get_ocr_engine().recognize(image)