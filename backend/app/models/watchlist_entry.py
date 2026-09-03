import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Date, Index
from app.db.base import Base


class WatchlistEntryModel(Base):
    __tablename__ = "watchlist_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_number = Column(String(64), index=True, nullable=True)
    name = Column(String(128), index=True, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(64), nullable=True)
    reason = Column(Text, nullable=False)
    severity = Column(String(32), default="CRITICAL", nullable=False)
    source = Column(String(64), default="INTERPOL_RED_NOTICE", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_watchlist_search", "document_number", "name"),
    )
