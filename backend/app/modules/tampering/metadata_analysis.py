"""Supporting image metadata analysis; absence of metadata is not suspicious."""

from pathlib import Path
from PIL import Image, ExifTags
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    """Return supporting metadata evidence and availability metrics."""
    with Image.open(context.image_path) as image:
        exif = {ExifTags.TAGS.get(key, str(key)): value for key, value in image.getexif().items()}
        info = dict(image.info)
    software = str(exif.get("Software") or info.get("Software") or "").strip()
    date_original = str(exif.get("DateTimeOriginal") or "").strip()
    date_modified = str(exif.get("DateTime") or "").strip()
    metadata = {
        "metadata_available": bool(exif or info),
        "exif_field_count": len(exif),
        "format": Path(context.image_path).suffix.lower().lstrip("."),
        "software": software or "unavailable",
        "timestamp_original": date_original or "unavailable",
        "timestamp_modified": date_modified or "unavailable",
    }
    evidence: list[EvidenceItem] = []
    editing_terms = ("photoshop", "gimp", "lightroom", "affinity", "canva", "pixlr")
    if software and any(term in software.lower() for term in editing_terms):
        evidence.append(EvidenceItem(
            screening_id=context.screening_id, module_name="tampering", category="METADATA_EDITING_SOFTWARE",
            severity="LOW", source="tampering.metadata_analysis", confidence=0.45,
            description="Image metadata identifies editing software; this is supporting evidence only.", metrics=metadata,
        ))
    if date_original and date_modified and date_modified < date_original:
        evidence.append(EvidenceItem(
            screening_id=context.screening_id, module_name="tampering", category="METADATA_TIMESTAMP_INCONSISTENCY",
            severity="LOW", source="tampering.metadata_analysis", confidence=0.55,
            description="Image metadata timestamps are internally inconsistent; this is supporting evidence only.", metrics=metadata,
        ))
    return evidence, "SUCCESS", metadata
