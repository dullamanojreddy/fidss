def compute_check_digit(data: str) -> int:
    """
    Implement the ICAO 9303 weighted 7-3-1 mod-10 check digit algorithm.
    """
    weights = [7, 3, 1]
    total = 0
    for i, c in enumerate(data):
        if c == '<':
            val = 0
        elif '0' <= c <= '9':
            val = int(c)
        elif 'A' <= c <= 'Z':
            val = ord(c) - ord('A') + 10
        else:
            val = 0
        total += val * weights[i % 3]
    return total % 10

def verify_check_digit(data: str, check_digit: str) -> bool:
    if not check_digit or not data:
        return False
    if len(check_digit) != 1:
        return False
    expected = 0 if check_digit == '<' else int(check_digit) if check_digit.isdigit() else None
    if expected is None:
        return False
    return compute_check_digit(data) == expected
