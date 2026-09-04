import pytest
from app.modules.validation.watchlist import check_watchlist
from app.providers.watchlist.local_provider import LocalSyntheticWatchlistProvider
from app.modules.validation.duplicate_identity import check_duplicate_identity

class MockFailingProvider:
    def search(self, document_number, name, dob):
        raise Exception("Database connection failed")

def test_watchlist_exact_document_number():
    provider = LocalSyntheticWatchlistProvider() # Uses default synthetic file
    findings = check_watchlist("FAKE12345", "SOME OTHER NAME", "2000-01-01", provider)
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert findings[0]["category"] == "WATCHLIST_MATCH"
    assert "Exact document number match" in findings[0]["description"]

def test_watchlist_fuzzy_name_dob():
    provider = LocalSyntheticWatchlistProvider()
    findings = check_watchlist("NOT_IN_DB", "JOHN  BADGUY", "1990-05-15", provider)
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert "Name fuzzy match" in findings[0]["description"]

def test_watchlist_fuzzy_name_alone():
    provider = LocalSyntheticWatchlistProvider()
    # Name matches, but DOB does not match
    findings = check_watchlist("NOT_IN_DB", "JOHN  BADGUY", "1999-12-31", provider)
    assert len(findings) == 0

def test_watchlist_no_match():
    provider = LocalSyntheticWatchlistProvider()
    findings = check_watchlist("CLEAN123", "CLEAN NAME", "2000-01-01", provider)
    assert len(findings) == 0

def test_watchlist_unavailable():
    provider = MockFailingProvider()
    findings = check_watchlist("CLEAN123", "CLEAN NAME", "2000-01-01", provider)
    assert len(findings) == 1
    assert findings[0]["category"] == "WATCHLIST_UNAVAILABLE"
    assert findings[0]["severity"] == "LOW"
    assert "Could not perform watchlist check" in findings[0]["description"]

# DUPLICATE IDENTITY TESTS
def test_duplicate_exact_doc():
    curr = {"document_number": "DOC123", "screening_id": "S1"}
    hist = [{"document_number": "DOC123", "screening_id": "S2"}]
    findings = check_duplicate_identity(curr, hist)
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"

def test_duplicate_same_name_dob_diff_doc():
    curr = {"document_number": "DOC1", "name": "JOHN DOE", "dob": "1990-01-01", "screening_id": "S1"}
    hist = [{"document_number": "DOC2", "name": "JOHN DOE", "dob": "1990-01-01", "screening_id": "S2"}]
    findings = check_duplicate_identity(curr, hist)
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"

def test_duplicate_no_match():
    curr = {"document_number": "DOC1", "name": "JOHN DOE", "dob": "1990-01-01", "screening_id": "S1"}
    hist = [{"document_number": "DOC2", "name": "JANE DOE", "dob": "1991-01-01", "screening_id": "S2"}]
    findings = check_duplicate_identity(curr, hist)
    assert len(findings) == 0

def test_duplicate_empty_historical():
    curr = {"document_number": "DOC1", "screening_id": "S1"}
    findings = check_duplicate_identity(curr, [])
    assert len(findings) == 0

def test_duplicate_exclude_self():
    curr = {"document_number": "DOC1", "screening_id": "S1"}
    hist = [{"document_number": "DOC1", "screening_id": "S1"}]
    findings = check_duplicate_identity(curr, hist)
    assert len(findings) == 0
