import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class DocumentField(Base):
    __tablename__ = "document_fields"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_id = Column(String(36), ForeignKey("screenings.id"), index=True, nullable=False)
    field_name = Column(String(64), nullable=False)
    field_value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    source = Column(String(32), default="OCR", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    screening = relationship("Screening", back_populates="document_fields")

    __table_args__ = (
        Index("idx_doc_field_search", "screening_id", "field_name"),
    )
