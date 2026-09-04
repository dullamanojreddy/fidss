import unicodedata
from typing import Dict, Any, List
from .config_loader import load_validation_config

def _normalize_name(name: str) -> str:
    if not name:
        return ""
    # Strip MRZ fillers and spaces
    name = name.replace("<", " ").strip()
    # Uppercase
    name = name.upper()
    # Strip diacritics
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                  if unicodedata.category(c) != 'Mn')
    # Remove extra spaces
    return " ".join(name.split())

def cross_validate(ocr_fields: Dict[str, Any], mrz_fields: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compares OCR-extracted visual fields against MRZ-parsed fields.
    Note: The field keys (document_number, surname, given_names, date_of_birth, date_of_expiry, nationality) 
    are assumed pending Person 1's real OCR output, and can be easily remapped later if their actual keys differ.
    """
    if not ocr_fields or not mrz_fields:
        return []

    findings = []

    def add_finding(field: str, ocr_val: str, mrz_val: str, severity: str):
        findings.append({
            "category": "MRZ_OCR_MISMATCH",
            "severity": severity,
            "source": "cross_validator",
            "confidence": load_validation_config()["cross_validator_exact_mismatch_confidence"],
            "description": f"Mismatch in {field}. OCR: '{ocr_val}', MRZ: '{mrz_val}'",
            "metrics": {
                "ocr_value": ocr_val,
                "mrz_value": mrz_val
            }
        })

    comparisons = [
        ("document_number", "HIGH", lambda o, m: str(o).strip().upper() == str(m).strip().upper()),
        ("date_of_birth", "HIGH", lambda o, m: str(o) == str(m)),
        ("date_of_expiry", "HIGH", lambda o, m: str(o) == str(m)),
        ("nationality", "MEDIUM", lambda o, m: str(o).strip().upper() == str(m).strip().upper())
    ]

    for field, severity, comp_fn in comparisons:
        if field in ocr_fields and field in mrz_fields:
            ocr_val = ocr_fields[field]
            mrz_val = mrz_fields[field]
            if ocr_val is not None and mrz_val is not None:
                if not comp_fn(ocr_val, mrz_val):
                    add_finding(field, str(ocr_val), str(mrz_val), severity)

    # Name match
    has_ocr_name = "surname" in ocr_fields or "given_names" in ocr_fields
    has_mrz_name = "surname" in mrz_fields or "given_names" in mrz_fields

    if has_ocr_name and has_mrz_name:
        ocr_surname = ocr_fields.get("surname", "") or ""
        ocr_given = ocr_fields.get("given_names", "") or ""
        mrz_surname = mrz_fields.get("surname", "") or ""
        mrz_given = mrz_fields.get("given_names", "") or ""

        ocr_full = f"{ocr_surname} {ocr_given}".strip()
        mrz_full = f"{mrz_surname} {mrz_given}".strip()

        ocr_norm = _normalize_name(ocr_full)
        mrz_norm = _normalize_name(mrz_full)

        if ocr_norm or mrz_norm:
            ocr_words = set(ocr_norm.split())
            mrz_words = set(mrz_norm.split())
            if ocr_words != mrz_words:
                add_finding("name", ocr_full, mrz_full, "CRITICAL")

    return findings
