from __future__ import annotations

import time

from app.schemas.document_context import DocumentContext
from app.schemas.module_result import ModuleResult
from app.schemas.evidence_item import EvidenceItem, BoundingBox

from .field_mapper import map_fields
from .ocr_engine import run_ocr
from .preprocess import preprocess_image


def analyze(context: DocumentContext) -> ModuleResult:
    """
    Run the complete OCR pipeline.

    Pipeline:
        image
        -> preprocessing
        -> OCR
        -> field mapping
        -> ModuleResult
    """
    start = time.perf_counter()

    try:
        # -----------------------------------------------------
        # 1. Preprocess
        # -----------------------------------------------------

        image = preprocess_image(context.image_path)

        # -----------------------------------------------------
        # 2. OCR
        # -----------------------------------------------------

        ocr_lines = run_ocr(image)

        if not ocr_lines:
            elapsed = int(
                (time.perf_counter() - start) * 1000
            )

            return ModuleResult(
                module="ocr",
                status="PARTIAL",
                evidence_items=[],
                processing_time_ms=elapsed,
                errors=["No text detected by OCR"],
                metadata={
                    "raw_lines": [],
                    "extracted_fields": {},
                },
            )

        # -----------------------------------------------------
        # 3. Convert OCR results into dictionaries
        # -----------------------------------------------------

        raw_lines = []

        for line in ocr_lines:
            raw_lines.append(
                {
                    "text": line.text,
                    "confidence": line.confidence,
                    "bbox": line.bbox,
                }
            )

        # -----------------------------------------------------
        # 4. Map OCR text to semantic fields
        # -----------------------------------------------------

        extracted_fields = map_fields(
            raw_lines,
            document_type=context.document_type,
            image_width=image.shape[1],
            image_height=image.shape[0],
        )

        # -----------------------------------------------------
        # 5. Generate OCR evidence
        # -----------------------------------------------------

        evidence_items: list[EvidenceItem] = []

        for line in ocr_lines:
            bbox = line.bbox

            # PaddleOCR returns four corner points:
            #
            # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            #
            # Convert that into our shared BoundingBox format.

            if len(bbox) == 4:
                xs = [point[0] for point in bbox]
                ys = [point[1] for point in bbox]

                x_min = int(min(xs))
                y_min = int(min(ys))
                x_max = int(max(xs))
                y_max = int(max(ys))

                document_region = BoundingBox(
                    x=x_min,
                    y=y_min,
                    width=max(0, x_max - x_min),
                    height=max(0, y_max - y_min),
                    label="OCR_TEXT",
                )
            else:
                document_region = None

            evidence_items.append(
                EvidenceItem(
                    screening_id=context.screening_id,
                    module_name="ocr",
                    category="OCR_TEXT",
                    severity="LOW",
                    source="PaddleOCR",
                    confidence=max(
                        0.0,
                        min(1.0, line.confidence),
                    ),
                    description=f"OCR detected text: {line.text}",
                    document_region=document_region,
                    metrics={
                        "ocr_confidence": line.confidence,
                    },
                )
            )

        elapsed = int(
            (time.perf_counter() - start) * 1000
        )

        # -----------------------------------------------------
        # 6. Return contract-compatible result
        # -----------------------------------------------------

        return ModuleResult(
            module="ocr",
            status="SUCCESS",
            evidence_items=evidence_items,
            processing_time_ms=elapsed,
            errors=[],
            metadata={
                # P2 expects these at the top level.
                "raw_lines": raw_lines,
                **extracted_fields,

                # P5's ModuleDispatcher.run_ocr()
                # expects this nested object.
                "extracted_fields": extracted_fields,
            },
        )

    except Exception as exc:
        elapsed = int(
            (time.perf_counter() - start) * 1000
        )

        return ModuleResult(
            module="ocr",
            status="FAILED",
            evidence_items=[],
            processing_time_ms=elapsed,
            errors=[str(exc)],
            metadata={},
        )