from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field


class SystemSettingsUpdate(BaseModel):
    settings: dict[str, Any] = Field(..., description="Key-value threshold configurations")


class SystemSettingsResponse(BaseModel):
    settings: dict[str, Any]
    last_updated_at: datetime | None = None
    updated_by: str | None = None
