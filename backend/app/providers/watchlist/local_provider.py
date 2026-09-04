import json
import os
from rapidfuzz import fuzz
from typing import List, Dict, Optional
from .base import WatchlistProvider
from app.modules.validation.config_loader import load_validation_config

class LocalSyntheticWatchlistProvider(WatchlistProvider):
    def __init__(self, file_path: str = None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "synthetic_watchlist.json")
        self.file_path = file_path
        self._records = []
        self.load_records()

    def load_records(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._records = data.get("records", [])
        except Exception as e:
            raise Exception(f"Failed to load synthetic watchlist: {e}")

    def search(self, document_number: Optional[str], name: Optional[str], dob: Optional[str]) -> List[Dict[str, str]]:
        matches = []
        search_doc = document_number.strip().upper() if document_number else None
        search_name = name.strip().upper() if name else None
        search_dob = dob.strip() if dob else None

        for rec in self._records:
            rec_doc = rec.get("document_number", "").strip().upper()
            rec_name = rec.get("name", "").strip().upper()
            rec_dob = rec.get("dob", "").strip()
            
            # Exact document number match
            if search_doc and search_doc == rec_doc:
                matches.append({
                    "matched_field": "document_number",
                    "matched_value": rec_doc,
                    "watchlist_entry_id": rec.get("id"),
                    "reason": "Exact document number match",
                    "score": 100.0
                })
                continue
                
            # Fuzzy name + DOB match
            if search_name and search_dob and rec_name and rec_dob:
                if search_dob == rec_dob:
                    score = fuzz.token_sort_ratio(search_name, rec_name)
                    if score >= load_validation_config()["fuzzy_name_match_threshold"]:
                        matches.append({
                            "matched_field": "name_and_dob",
                            "matched_value": f"{rec_name} / {rec_dob}",
                            "watchlist_entry_id": rec.get("id"),
                            "reason": f"Name fuzzy match ({score:.2f}) with exact DOB match",
                            "score": score
                        })
        return matches
