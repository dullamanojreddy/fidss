from datetime import date
from pydantic import BaseModel, Field


class WatchlistEntry(BaseModel):
    id: str
    document_number: str | None = None
    name: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    reason: str
    severity: str = "CRITICAL"
    source: str = "SYNTHETIC_INTERPOL_RED_NOTICE"
    is_synthetic: bool = True


class WatchlistSearchResult(BaseModel):
    matched: bool = False
    matches: list[WatchlistEntry] = []
    message: str = "No watchlist hits."
    is_synthetic_data: bool = True
