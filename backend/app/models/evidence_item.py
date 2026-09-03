import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class EvidenceItemModel(Base):
    __tablename__ = "evidence_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_id = Column(String(36), ForeignKey("screenings.id"), index=True, nullable=False)
    module_result_id = Column(String(36), ForeignKey("module_results.id"), index=True, nullable=True)
    module_name = Column(String(64), index=True, nullable=False)
    category = Column(String(64), nullable=False)
    severity = Column(String(32), default="INFO", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    source = Column(String(64), nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    description = Column(Text, nullable=False)
    region_json = Column(Text, nullable=True)
    metrics_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    screening = relationship("Screening", back_populates="evidence_items")
    module_result = relationship("ModuleResultModel", back_populates="evidence_items")

    __table_args__ = (
        Index("idx_evidence_severity", "screening_id", "severity"),
    )
