import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_number = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)  # PENDING, PROCESSING, COMPLETED, FAILED
    document_type = Column(String(32), default="passport", nullable=False)
    nationality = Column(String(64), default="IND (India)", nullable=True)
    overall_risk_score = Column(Float, default=0.0, nullable=False)
    screening_level = Column(String(32), default="CLEAR", index=True, nullable=False)  # CLEAR, REVIEW_RECOMMENDED, ENHANCED_REVIEW_RECOMMENDED, INCONCLUSIVE
    recommendation_text = Column(String(512), default="Screening completed.", nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    creator = relationship("User", back_populates="screenings", foreign_keys=[created_by])
    document = relationship("Document", back_populates="screening", uselist=False, cascade="all, delete-orphan")
    document_fields = relationship("DocumentField", back_populates="screening", cascade="all, delete-orphan")
    module_results = relationship("ModuleResultModel", back_populates="screening", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItemModel", back_populates="screening", cascade="all, delete-orphan")
    officer_review = relationship("OfficerReview", back_populates="screening", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="screening", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_screening_perf", "created_at", "screening_level"),
    )
