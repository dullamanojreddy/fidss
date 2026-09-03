from typing import Literal, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.schemas.evidence_item import EvidenceItem


class ModuleResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    module: str
    status: Literal["SUCCESS", "PARTIAL", "FAILED", "INCONCLUSIVE"]
    evidence_items: list[EvidenceItem] = []
    processing_time_ms: int | None = None
    errors: list[str] = []
    metadata: dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
