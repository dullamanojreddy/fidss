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
        device="cpu",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
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

        result = self._ocr.predict(image)

        lines: list[OCRLine] = []

        for page in result:
            data: dict[str, Any] = page.json

            # PaddleOCR 3.x stores the useful OCR information
            # inside the `res` object.
            res = data.get("res", {})

            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])
            boxes = res.get("rec_polys", [])

            for text, score, box in zip(texts, scores, boxes):
                text = str(text).strip()

                if not text:
                    continue

                lines.append(
                    OCRLine(
                        text=text,
                        confidence=float(score),
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