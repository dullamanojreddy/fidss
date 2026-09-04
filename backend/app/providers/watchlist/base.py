from typing import Protocol, List, Dict, Optional

class WatchlistProvider(Protocol):
    def search(self, document_number: Optional[str], name: Optional[str], dob: Optional[str]) -> List[Dict[str, str]]:
        ...
