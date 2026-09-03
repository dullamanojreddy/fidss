from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    label: str | None = None


class EvidenceItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    screening_id: UUID
    module_name: str = Field(..., description="Module that generated this evidence item")
    module_result_id: UUID | None = Field(default=None, description="FK provenance to ModuleResult execution")
    category: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    source: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    document_region: BoundingBox | None = None
    metrics: dict[str, float | str | int | bool] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
