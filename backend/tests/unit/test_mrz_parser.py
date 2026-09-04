import pytest
from app.modules.validation.mrz_parser import parse_mrz

def test_parse_td3_valid():
    lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<08"
    ]
    res = parse_mrz(lines)
    assert res.mrz_type == "TD3"
    assert res.document_type.value == "P"
    assert res.issuing_country.value == "UTO"
    assert res.surname.value == "ERIKSSON"
    assert res.given_names.value == "ANNA MARIA"
    assert res.document_number.value == "L898902C3"
    assert res.document_number.status == "VALID"
    assert res.nationality.value == "UTO"
    assert res.dob.value == "740812"
    assert res.dob.status == "VALID"
    assert res.sex.value == "F"
    assert res.expiry_date.value == "120415"
    assert res.expiry_date.status == "VALID"
    assert res.composite_status == "VALID"

def test_parse_td3_invalid_checksums():
    lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C37UTO7408123F1204151<<<<<<<<<<<<<<09" # tweaked checksums
    ]
    res = parse_mrz(lines)
    assert res.mrz_type == "TD3"
    assert res.document_number.status == "INVALID"
    assert res.dob.status == "INVALID"
    assert res.expiry_date.status == "INVALID"
    assert res.composite_status == "INVALID"

def test_parse_garbage():
    lines = ["THIS IS NOT AN MRZ", "REALLY NOT"]
    res = parse_mrz(lines)
    assert res.mrz_type == "UNKNOWN"
    assert res.document_type.status == "INCOMPLETE"
    assert res.composite_status == "INCOMPLETE"

def test_parse_td1_valid():
    lines = [
        "I<UTOD231458907<<<<<<<<<<<<<<<",
        "7408122F1204159UTO<<<<<<<<<<<6",
        "ERIKSSON<<ANNA<MARIA<<<<<<<<<<"
    ]
    res = parse_mrz(lines)
    assert res.mrz_type == "TD1"
    assert res.document_type.value == "I"
    assert res.issuing_country.value == "UTO"
    assert res.document_number.value == "D23145890"
    assert res.document_number.status == "VALID"
    assert res.dob.value == "740812"
    assert res.dob.status == "VALID"
    assert res.expiry_date.value == "120415"
    assert res.expiry_date.status == "VALID"
    assert res.composite_status == "VALID"
