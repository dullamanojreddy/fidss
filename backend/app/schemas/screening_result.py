from typing import Literal, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.evidence_item import EvidenceItem
from app.schemas.module_result import ModuleResult


ScreeningLevel = Literal["CLEAR", "REVIEW_RECOMMENDED", "ENHANCED_REVIEW_RECOMMENDED", "INCONCLUSIVE"]
ScreeningStatus = Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"]


class ExtractedField(BaseModel):
    name: str
    value: str
    confidence: float = 1.0
    source: str = "OCR"


class ScreeningResultResponse(BaseModel):
    id: UUID
    screening_number: str
    status: ScreeningStatus
    document_type: str
    nationality: str | None = None
    overall_risk_score: float = Field(ge=0.0, le=100.0)
    screening_level: ScreeningLevel
    recommendation_text: str
    document_id: UUID
    document_preview_url: str | None = None
    submitted_by: str | None = None
    submitted_at: datetime
    completed_at: datetime | None = None
    extracted_fields: dict[str, str] = Field(default_factory=dict)
    module_results: list[ModuleResult] = Field(default_factory=list)
    key_findings: list[EvidenceItem] = Field(default_factory=list)
    total_evidence_count: int = 0
    current_step: int = 7


class ScreeningListItem(BaseModel):
    id: UUID
    screening_number: str
    document_type: str
    submitted_at: datetime
    screening_level: ScreeningLevel
    overall_risk_score: float
    status: ScreeningStatus
    submitted_by: str | None = None
