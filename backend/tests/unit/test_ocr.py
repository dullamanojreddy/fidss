import uuid

from app.modules.ocr.field_mapper import map_fields
from app.modules.ocr.normalizer import (
    normalize_country,
    normalize_date,
    normalize_name,
)
from app.schemas.document_context import DocumentContext
from app.modules.ocr.analyze import analyze


def test_normalizer():
    assert normalize_name("José García") == "JOSE GARCIA"
    assert normalize_date("04/09/2026") == "2026-09-04"
    assert normalize_country("India") == "IND"


def test_field_mapper():
    lines = [
        {"text": "PASSPORT NO: A1234567"},
        {"text": "SURNAME: TEST"},
        {"text": "GIVEN NAMES: ANANYA"},
        {"text": "DATE OF BIRTH: 15/08/2004"},
        {"text": "DATE OF EXPIRY: 15/08/2034"},
        {"text": "NATIONALITY: INDIA"},
    ]

    fields = map_fields(lines, "passport")

    assert fields["document_number"] == "A1234567"
    assert fields["surname"] == "TEST"
    assert fields["given_names"] == "ANANYA"
    assert fields["date_of_birth"] == "2004-08-15"
    assert fields["date_of_expiry"] == "2034-08-15"
    assert fields["nationality"] == "IND"
    assert fields["name"] == "TEST ANANYA"


def test_ocr_analyze():
    from pathlib import Path
    img_path = Path(__file__).resolve().parent.parent.parent / "test_document.jpg"
    context = DocumentContext(
        screening_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        image_path=str(img_path) if img_path.exists() else "test_document.jpg",
        document_type="passport",
        image_sha256="test",
    )

    result = analyze(context)

    assert result.status == "SUCCESS"
    assert len(result.evidence_items) > 0
    assert result.metadata["raw_lines"]
    assert "extracted_fields" in result.metadata
    assert result.metadata["extracted_fields"].get("document_number") == "A1234567"
    assert result.metadata["extracted_fields"].get("Passport Number") == "A1234567"

def test_spatial_field_mapping():
    lines = [
        {
            "text": "A1234567",
            "confidence": 0.99,
            "bbox": [
                [600, 60],
                [750, 60],
                [750, 100],
                [600, 100],
            ],
        }
    ]

    fields = map_fields(
        lines,
        document_type="passport",
        image_width=900,
        image_height=600,
    )

    assert fields["document_number"] == "A1234567"