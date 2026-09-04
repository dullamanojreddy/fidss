from typing import List, Dict, Optional
from app.providers.watchlist.base import WatchlistProvider

def check_watchlist(document_number: Optional[str], name: Optional[str], dob: Optional[str], provider: WatchlistProvider) -> List[Dict]:
    try:
        matches = provider.search(document_number, name, dob)
    except Exception as e:
        return [{
            "category": "WATCHLIST_UNAVAILABLE",
            "severity": "LOW",
            "source": "watchlist",
            "description": f"Could not perform watchlist check: {str(e)}",
            "metrics": {}
        }]
        
    findings = []
    for match in matches:
        score = match.get("score", 0.0)
        confidence = score / 100.0 if score > 1.0 else score
        
        findings.append({
            "category": "WATCHLIST_MATCH",
            "severity": "CRITICAL",
            "source": "watchlist",
            "confidence": confidence,
            "description": f"Prototype/synthetic watchlist match: {match.get('reason')}",
            "metrics": match
        })
        
    return findings
