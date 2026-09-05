import re
from typing import Optional, List

def detect_mrz(lines: List[str]) -> Optional[List[str]]:
    """
    Given raw OCR text lines, detect whether an MRZ zone is present.
    Returns the MRZ lines if found, or None otherwise.
    """
    # Look for 2 or 3 consecutive lines of length 30, 36, or 44
    # that consist mostly of A-Z, 0-9, and <
    # We allow slight OCR length variations or noise by checking if a substring matches.
    # But usually, OCR returns the full line. Let's do a strict-ish check first.
    
    # MRZ lines should be at the bottom, so we can search from bottom up,
    # or just find any consecutive block.
    
    valid_lengths = {30, 36, 44}
    mrz_pattern = re.compile(r'^[A-Z0-9<]+$')
    
    # Let's clean lines (strip whitespace), handling both strings and OCR line dicts
    cleaned_lines = []
    for line in lines:
        text = line.get("text", "") if isinstance(line, dict) else str(line)
        cleaned = text.strip().replace(" ", "").upper()
        if cleaned:
            cleaned_lines.append(cleaned)
    
    # Find longest block of valid MRZ lines
    for expected_count, expected_length in [(2, 44), (2, 36), (3, 30)]:
        for i in range(len(cleaned_lines) - expected_count + 1):
            block = cleaned_lines[i:i+expected_count]
            # check if all lines in block have the right length and pattern
            if all(len(b) == expected_length and mrz_pattern.match(b) for b in block):
                return block
                
    # If perfect match fails, maybe tolerate some characters (like O instead of 0, but regex handles both)
    # What if lengths are slightly off due to OCR missing a '<'? 
    # For this isolated sub-task, exact match on A-Z0-9< and length is usually the baseline.
    
    return None
