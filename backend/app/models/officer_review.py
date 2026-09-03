import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class OfficerReview(Base):
    __tablename__ = "officer_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_id = Column(String(36), ForeignKey("screenings.id"), unique=True, index=True, nullable=False)
    officer_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    decision = Column(String(32), nullable=False)  # ACCEPT, REJECT, ESCALATE, REQUEST_RECAPTURE, MARK_INCONCLUSIVE
    reason = Column(String(128), nullable=False)
    notes = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    screening = relationship("Screening", back_populates="officer_review")
    officer = relationship("User", back_populates="reviews")
