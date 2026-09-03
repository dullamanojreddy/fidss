from typing import Protocol, runtime_checkable
from datetime import date
from app.schemas.watchlist import WatchlistSearchResult


@runtime_checkable
class WatchlistProvider(Protocol):
    def search(
        self,
        document_number: str | None = None,
        name: str | None = None,
        dob: date | None = None,
    ) -> WatchlistSearchResult:
        """Search watchlist provider for matching entries."""
        ...
