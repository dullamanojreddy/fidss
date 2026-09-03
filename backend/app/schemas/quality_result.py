from typing import Literal
from pydantic import BaseModel, Field


class QualityResult(BaseModel):
    status: Literal["PASS", "WARNING", "FAIL"] = "PASS"
    blur_score: float = Field(default=100.0, description="Laplacian variance or sharpness score")
    brightness_score: float = Field(default=128.0, description="Mean luminance score (0-255)")
    resolution_ok: bool = True
    document_detected: bool = True
    orientation: str = "0_DEG"
    quality_issues: list[str] = []
