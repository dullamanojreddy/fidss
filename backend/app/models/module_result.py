import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class ModuleResultModel(Base):
    __tablename__ = "module_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_id = Column(String(36), ForeignKey("screenings.id"), index=True, nullable=False)
    module_name = Column(String(64), nullable=False)
    status = Column(String(32), default="SUCCESS", nullable=False)  # SUCCESS, PARTIAL, FAILED, INCONCLUSIVE
    processing_time_ms = Column(Integer, default=0, nullable=False)
    errors_json = Column(Text, default="[]", nullable=False)
    metadata_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    screening = relationship("Screening", back_populates="module_results")
    evidence_items = relationship("EvidenceItemModel", back_populates="module_result", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_mod_result_screening", "screening_id", "module_name"),
    )
