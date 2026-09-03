from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.watchlist import WatchlistSearchResult, WatchlistEntry
from app.models.watchlist_entry import WatchlistEntryModel

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("/search", response_model=WatchlistSearchResult)
def search_watchlist(
    query: Optional[str] = Query(None, description="Document number or traveler name"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Database-driven watchlist search querying persistent database records."""
    db_query = db.query(WatchlistEntryModel)
    if query:
        q = f"%{query.strip().upper()}%"
        db_query = db_query.filter(
            or_(
                WatchlistEntryModel.document_number.ilike(q),
                WatchlistEntryModel.name.ilike(q),
            )
        )

    records = db_query.limit(50).all()
    results = [
        WatchlistEntry(
            id=r.id,
            document_number=r.document_number,
            name=r.name,
            date_of_birth=r.date_of_birth,
            nationality=r.nationality,
            reason=r.reason,
            severity=r.severity,
            source=r.source,
            is_synthetic=False,
        )
        for r in records
    ]

    matched = len(results) > 0 and bool(query)
    message = (
        f"Found {len(results)} matching database record(s)."
        if results
        else "No watchlist matches found in database."
    )

    return WatchlistSearchResult(
        matched=matched,
        matches=results,
        message=message,
        is_synthetic_data=False,
    )
