from typing import Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

OfficerDecision = Literal["ACCEPT", "REJECT", "ESCALATE", "REQUEST_RECAPTURE", "MARK_INCONCLUSIVE"]


class OfficerReviewCreate(BaseModel):
    decision: OfficerDecision
    reason: str = Field(..., min_length=2, max_length=128)
    notes: str = Field(default="", max_length=2000)


class OfficerReviewResponse(BaseModel):
    id: UUID
    screening_id: UUID
    officer_id: UUID
    officer_name: str | None = None
    decision: OfficerDecision
    reason: str
    notes: str
    created_at: datetime
