from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.quality_result import QualityResult


class DocumentContext(BaseModel):
    screening_id: UUID
    document_id: UUID
    image_path: str
    document_type: str = "passport"
    image_sha256: str
    selfie_path: str | None = None
    quality_result: QualityResult | None = None
    ocr_result: dict[str, Any] | None = None
    mrz_result: dict[str, Any] | None = None
    validation_result: dict[str, Any] | None = None
    allowed_outputs: dict[str, Any] = Field(default_factory=dict)
