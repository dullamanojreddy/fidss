import time

from app.schemas.document_context import DocumentContext
from app.schemas.quality_result import QualityResult

from .quality_checker import analyze_quality


def analyze(context: DocumentContext) -> QualityResult:
    """
    Entry point for Person 1's quality module.

    The dispatcher calls this function before OCR.
    """

    start_time = time.time()

    result = analyze_quality(context.image_path)

    # QualityResult doesn't currently have processing_time_ms,
    # so timing is intentionally not inserted into the schema.
    _processing_time_ms = int(
        (time.time() - start_time) * 1000
    )

    return result