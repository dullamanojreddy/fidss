import pytest
from app.modules.validation.mrz_detector import detect_mrz

def test_detect_mrz_td3():
    lines = [
        "SOME RANDOM HEADER OCR TEXT",
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
        "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<08",
        "SOME FOOTER TEXT"
    ]
    result = detect_mrz(lines)
    assert result is not None
    assert len(result) == 2
    assert result[0].startswith("P<UTO")

def test_detect_mrz_td1():
    lines = [
        "I<UTOD231458907<<<<<<<<<<<<<<<",
        "7408122F1204159UTO<<<<<<<<<<<6",
        "ERIKSSON<<ANNA<MARIA<<<<<<<<<<"
    ]
    result = detect_mrz(lines)
    assert result is not None
    assert len(result) == 3
    assert result[0].startswith("I<UTO")

def test_detect_mrz_not_found():
    lines = [
        "DRIVING LICENCE",
        "NAME: JOHN DOE",
        "DOB: 1980-01-01"
    ]
    assert detect_mrz(lines) is None
    
def test_detect_mrz_with_spaces():
    lines = [
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<< ",
        "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<08"
    ]
    result = detect_mrz(lines)
    assert result is not None
    assert len(result) == 2
