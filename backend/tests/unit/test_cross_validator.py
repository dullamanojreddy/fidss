import pytest
from app.modules.validation.cross_validator import cross_validate, _normalize_name

def test_fully_matching_fields():
    ocr = {
        "document_number": "A1234567",
        "date_of_birth": "1990-01-01",
        "date_of_expiry": "2030-01-01",
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    mrz = {
        "document_number": "A1234567",
        "date_of_birth": "1990-01-01",
        "date_of_expiry": "2030-01-01",
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 0

def test_document_number_mismatch():
    ocr = {"document_number": "A1234567"}
    mrz = {"document_number": "B1234567"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"
    assert "document_number" in findings[0]["description"]

def test_date_of_birth_mismatch():
    ocr = {"date_of_birth": "1990-01-01"}
    mrz = {"date_of_birth": "1991-01-01"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"

def test_date_of_expiry_mismatch():
    ocr = {"date_of_expiry": "2030-01-01"}
    mrz = {"date_of_expiry": "2031-01-01"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"

def test_nationality_mismatch():
    ocr = {"nationality": "IND"}
    mrz = {"nationality": "USA"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 1
    assert findings[0]["severity"] == "MEDIUM"

def test_name_mismatch_critical():
    ocr = {"surname": "DOE", "given_names": "JOHN"}
    mrz = {"surname": "SMITH", "given_names": "ALEX"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert "name" in findings[0]["description"]

def test_name_mismatch_whitespace_diacritic_ordering_skipped():
    ocr = {"surname": "Doe", "given_names": "John  William"}
    mrz = {"surname": "JOHN", "given_names": "WILLIAM DOE"}
    # Words in OCR: DOE, JOHN, WILLIAM
    # Words in MRZ: JOHN, WILLIAM, DOE
    # Ordering shouldn't matter
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 0
    
    # Test diacritics
    ocr_diacritic = {"surname": "Müller"}
    mrz_diacritic = {"surname": "MULLER"}
    assert len(cross_validate(ocr_diacritic, mrz_diacritic)) == 0

def test_mrz_filler_stripped():
    ocr = {"surname": "DOE", "given_names": "JOHN"}
    mrz = {"surname": "DOE", "given_names": "JOHN<<<<<<<<<"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 0

def test_field_present_in_only_one_source():
    ocr = {"document_number": "A1234567"}
    mrz = {"date_of_birth": "1990-01-01"}
    findings = cross_validate(ocr, mrz)
    assert len(findings) == 0

def test_both_inputs_empty():
    assert len(cross_validate({}, {})) == 0
    assert len(cross_validate(None, None)) == 0
