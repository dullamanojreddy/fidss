import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Text, DateTime, Index
from app.db.base import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(64), index=True, nullable=False)
    version = Column(String(32), nullable=False)
    runtime = Column(String(32), default="ONNXRuntime-CPU", nullable=False)
    checksum = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
