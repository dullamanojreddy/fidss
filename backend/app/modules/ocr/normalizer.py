from __future__ import annotations

import re
import unicodedata
from datetime import datetime


def normalize_text(value: str) -> str:
    """Normalize whitespace and remove surrounding whitespace."""
    if not value:
        return ""

    value = str(value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_name(value: str) -> str:
    """
    Normalize a name for comparison.

    Display/original OCR text should be preserved separately.
    """
    value = normalize_text(value)

    # Remove accents/diacritics.
    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    # Keep alphabetic characters and spaces.
    value = re.sub(r"[^A-Za-z ]", "", value)

    return value.upper().strip()


def normalize_date(value: str) -> str:
    """
    Convert common OCR date formats to ISO YYYY-MM-DD.

    Returns the original normalized value if no supported
    format can be parsed.
    """
    value = normalize_text(value)

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d %m %Y",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return value


def normalize_country(value: str) -> str:
    """
    Normalize a country/nationality value for comparison.

    Known ISO alpha-3 values are preserved in uppercase.
    """
    value = normalize_text(value).upper()

    # Common OCR variants encountered for Indian documents.
    country_aliases = {
        "INDIA": "IND",
        "IND": "IND",
        "INDIAN": "IND",
    }

    return country_aliases.get(value, value)


def normalize_document_number(value: str) -> str:
    """Normalize a document number for comparison."""
    value = normalize_text(value).upper()

    # OCR sometimes introduces spaces around document numbers.
    value = re.sub(r"\s+", "", value)

    return value