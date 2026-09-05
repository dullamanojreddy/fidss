import unicodedata
from rapidfuzz import fuzz
from typing import List, Dict, Any
from .config_loader import load_validation_config

def _normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.upper()
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                  if unicodedata.category(c) != 'Mn')
    return " ".join(name.split())

def check_duplicate_identity(current: Dict[str, Any], historical_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not historical_records:
        return []
        
    findings = []
    
    curr_doc = current.get("document_number", "").strip().upper() if current.get("document_number") else ""
    curr_name = _normalize_name(current.get("name", ""))
    curr_dob = current.get("dob", "").strip() if current.get("dob") else ""
    curr_id = current.get("screening_id")
    
    for hist in historical_records:
        if curr_id and hist.get("screening_id") == curr_id:
            continue
            
        hist_doc = hist.get("document_number", "").strip().upper() if hist.get("document_number") else ""
        hist_name = _normalize_name(hist.get("name", ""))
        hist_dob = hist.get("dob", "").strip() if hist.get("dob") else ""
        hist_id = hist.get("screening_id", "UNKNOWN")
        
        # document_number exact match
        if curr_doc and hist_doc and curr_doc == hist_doc:
            name_similarity = fuzz.token_sort_ratio(curr_name, hist_name) if (curr_name and hist_name) else 100
            dob_mismatch = bool(curr_dob and hist_dob and curr_dob != hist_dob)

            if name_similarity < 70 or dob_mismatch:
                findings.append({
                    "category": "DUPLICATE_IDENTITY",
                    "severity": "CRITICAL",
                    "source": "duplicate_identity",
                    "confidence": 1.0,
                    "description": f"Document number {curr_doc} was previously associated with a different person ({hist_name or 'Unknown'}) in screening {hist_id}",
                    "metrics": {
                        "current_document_number": curr_doc,
                        "historical_document_number": hist_doc,
                        "historical_screening_id": hist_id,
                        "conflict": "identity_mismatch"
                    }
                })
            else:
                findings.append({
                    "category": "RECORD_FOUND",
                    "severity": "LOW",
                    "source": "duplicate_identity",
                    "confidence": 1.0,
                    "description": f"Document number matches previous screening {hist_id} for the same traveler.",
                    "metrics": {
                        "current_document_number": curr_doc,
                        "historical_document_number": hist_doc,
                        "historical_screening_id": hist_id,
                        "repeat_traveler": True
                    }
                })
            continue # Already handled this record
            
        # name similarity >= 85 AND DOB matches exactly
        if curr_name and hist_name and curr_dob and hist_dob:
            if curr_dob == hist_dob:
                score = fuzz.token_sort_ratio(curr_name, hist_name)
                if score >= load_validation_config()["duplicate_identity_name_threshold"]:
                    findings.append({
                        "category": "DUPLICATE_IDENTITY",
                        "severity": "HIGH",
                        "source": "duplicate_identity",
                        "confidence": score / 100.0,
                        "description": f"Name fuzzy match ({score:.2f}) and exact DOB match with historical screening {hist_id}",
                        "metrics": {
                            "current_name": current.get("name"),
                            "historical_name": hist.get("name"),
                            "dob": curr_dob,
                            "historical_screening_id": hist_id
                        }
                    })
                    
    return findings
