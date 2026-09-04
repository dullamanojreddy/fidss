import pytest
from datetime import datetime, timedelta
from app.modules.validation.rule_engine import validate_document, load_rules, RuleEngineError

def get_iso_date(days_offset):
    return (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")

def test_fully_valid_indian_passport():
    fields = {
        "document_number": "A1234567",
        "date_of_birth": "1990-01-01",
        "date_of_issue": get_iso_date(-1000),
        "date_of_expiry": get_iso_date(1000),
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = validate_document(fields, "passport", "IND")
    assert len(findings) == 0

def test_missing_required_field_passport():
    fields = {
        "document_number": "A1234567",
        # missing date_of_birth
        "date_of_issue": get_iso_date(-1000),
        "date_of_expiry": get_iso_date(1000),
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = validate_document(fields, "passport", "IND")
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"
    assert "date_of_birth" in findings[0]["fields"]

def test_bad_date_order_passport():
    fields = {
        "document_number": "A1234567",
        "date_of_birth": "1990-01-01",
        "date_of_issue": get_iso_date(100), # issue is after expiry
        "date_of_expiry": get_iso_date(50),
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = validate_document(fields, "passport", "IND")
    bad_order_findings = [f for f in findings if f["category"] == "validation" and "Date order mismatch" in f["description"]]
    assert len(bad_order_findings) >= 1
    assert bad_order_findings[0]["severity"] == "MEDIUM"

def test_expired_passport():
    fields = {
        "document_number": "A1234567",
        "date_of_birth": "1990-01-01",
        "date_of_issue": get_iso_date(-1000),
        "date_of_expiry": get_iso_date(-10), # EXPIRED
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = validate_document(fields, "passport", "IND")
    expired = [f for f in findings if f["description"] == "Document is EXPIRED"]
    assert len(expired) == 1
    assert expired[0]["severity"] == "CRITICAL"

def test_expiring_soon_passport():
    fields = {
        "document_number": "A1234567",
        "date_of_birth": "1990-01-01",
        "date_of_issue": get_iso_date(-1000),
        "date_of_expiry": get_iso_date(30), # EXPIRING SOON (<180 days)
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = validate_document(fields, "passport", "IND")
    expiring = [f for f in findings if "EXPIRING_SOON" in f["description"]]
    assert len(expiring) == 1
    assert expiring[0]["severity"] == "MEDIUM"

def test_bad_pattern_passport():
    fields = {
        "document_number": "12345ABC", # bad pattern
        "date_of_birth": "1990-01-01",
        "date_of_issue": get_iso_date(-1000),
        "date_of_expiry": get_iso_date(1000),
        "nationality": "IND",
        "surname": "DOE",
        "given_names": "JOHN"
    }
    findings = validate_document(fields, "passport", "IND")
    pattern_err = [f for f in findings if "pattern" in f["description"]]
    assert len(pattern_err) == 1
    assert pattern_err[0]["severity"] == "MEDIUM"
    assert "document_number" in pattern_err[0]["fields"]

def test_unknown_document_type():
    findings = validate_document({}, "alien_id", "IND")
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert "No rules file found" in findings[0]["description"]
    
    with pytest.raises(RuleEngineError):
        load_rules("alien_id", "IND")

def test_national_id_valid_and_no_expiry():
    fields = {
        "document_number": "9876 5432 1098", # valid format (2-9 start, 12 digits, spaces)
        "date_of_birth": "1990-01-01"
    }
    findings = validate_document(fields, "national_id", "IND")
    assert len(findings) == 0

def test_national_id_bad_pattern():
    fields = {
        "document_number": "0876 5432 1098", # invalid (starts with 0)
        "date_of_birth": "1990-01-01"
    }
    findings = validate_document(fields, "national_id", "IND")
    assert len(findings) == 1
    assert findings[0]["severity"] == "MEDIUM"

def test_passport_pattern_specifics():
    valid_patterns = ['A1234567', 'P9012345']
    invalid_patterns = ['AB123456', 'Q1234567', 'A0234567', 'A1234560']
    
    for pat in valid_patterns:
        fields = {
            'document_number': pat,
            'date_of_birth': '1990-01-01',
            'date_of_issue': get_iso_date(-1000),
            'date_of_expiry': get_iso_date(1000),
            'nationality': 'IND',
            'surname': 'DOE',
            'given_names': 'JOHN'
        }
        findings = validate_document(fields, 'passport', 'IND')
        pat_errs = [f for f in findings if 'pattern' in f['description'].lower()]
        assert len(pat_errs) == 0, f'Expected valid pattern {pat} but failed'

    for pat in invalid_patterns:
        fields = {
            'document_number': pat,
            'date_of_birth': '1990-01-01',
            'date_of_issue': get_iso_date(-1000),
            'date_of_expiry': get_iso_date(1000),
            'nationality': 'IND',
            'surname': 'DOE',
            'given_names': 'JOHN'
        }
        findings = validate_document(fields, 'passport', 'IND')
        pat_errs = [f for f in findings if 'pattern' in f['description'].lower()]
        assert len(pat_errs) == 1, f'Expected invalid pattern {pat} to fail but it passed'

def test_missing_date_field_skips_order_rule():
    # driving_license has date_order_rules using date_of_issue, but it's not in required_fields.
    fields = {
        'document_number': 'MH12 2011 0062821', 
        'date_of_birth': '1990-01-01',
        # date_of_issue is omitted
        'date_of_expiry': get_iso_date(1000)
    }
    findings = validate_document(fields, 'driving_license', 'IND')
    
    # It should not have any date order findings, and no CRITICAL findings.
    date_order_findings = [f for f in findings if 'date order' in f['description'].lower()]
    assert len(date_order_findings) == 0
    critical_findings = [f for f in findings if f['severity'] == 'CRITICAL']
    assert len(critical_findings) == 0
