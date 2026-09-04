import pytest
from app.modules.validation.mrz_checksum import compute_check_digit, verify_check_digit

def independent_compute_check_digit(data: str) -> int:
    """An independent implementation using a dictionary and modulo math to cross-check."""
    char_map = {str(i): i for i in range(10)}
    char_map.update({chr(i + 65): i + 10 for i in range(26)})
    char_map['<'] = 0
    
    weights = [7, 3, 1]
    total = sum(char_map.get(c, 0) * weights[idx % 3] for idx, c in enumerate(data))
    return total % 10

def test_checksum_algorithms_agree():
    test_cases = [
        "L898902C3",
        "740812",
        "120415",
        "<<<<<<<<<<<<<<",
        "L898902C3674081221204159<<<<<<<<<<<<<<0",
        "A1B2C3D4E5",
        "1234567890",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "<<<123<<<ABC<<<"
    ]
    for case in test_cases:
        assert compute_check_digit(case) == independent_compute_check_digit(case), f"Mismatch on {case}"

def test_verify_check_digit():
    assert verify_check_digit("L898902C3", "6") is True
    assert verify_check_digit("740812", "2") is True
    assert verify_check_digit("120415", "9") is True
    assert verify_check_digit("<<<<<<<<<<<<<<", "0") is True
    # Test failure
    assert verify_check_digit("L898902C3", "7") is False
    assert verify_check_digit("740812", "3") is False
    assert verify_check_digit("", "2") is False
    assert verify_check_digit("740812", "") is False

def test_icao_9303_sample():
    # Official ICAO 9303 Part 4 Appendix A sample (TD3)
    # The composite check digit for this standard sample is 8
    doc_no = "L898902C3"
    dob = "740812"
    expiry = "120415"
    personal_no = "<<<<<<<<<<<<<<"
    
    assert compute_check_digit(doc_no) == 6
    assert compute_check_digit(dob) == 2
    assert compute_check_digit(expiry) == 9
    assert compute_check_digit(personal_no) == 0
    
    composite_str = f"{doc_no}6{dob}2{expiry}9{personal_no}0"
    assert compute_check_digit(composite_str) == 8
