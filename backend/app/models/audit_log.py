import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    block_index = Column(Integer, autoincrement=True, unique=True, index=True)
    screening_id = Column(String(36), ForeignKey("screenings.id"), index=True, nullable=True)
    previous_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), unique=True, index=True, nullable=False)
    event_type = Column(String(64), index=True, nullable=False)
    event_payload_json = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    actor_id = Column(String(64), default="system", nullable=False)

    screening = relationship("Screening", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_chain_block", "block_index", "current_hash"),
    )
