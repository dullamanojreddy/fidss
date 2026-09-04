from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .normalizer import (
    normalize_country,
    normalize_date,
    normalize_document_number,
    normalize_name,
)


TEMPLATE_DIR = Path(__file__).parent / "layout_templates"

DATE_PATTERN = re.compile(
    r"\b(?:\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b"
)

DOCUMENT_NUMBER_PATTERN = re.compile(
    r"\b[A-Z0-9]{6,12}\b"
)


def load_template(document_type: str) -> dict[str, Any]:
    """Load the layout template for a document type."""

    template_path = TEMPLATE_DIR / f"{document_type.lower()}.json"

    if not template_path.exists():
        return {}

    try:
        with template_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


def _clean_line(text: str) -> str:
    return " ".join(str(text).strip().split())

def _bbox_center(
    bbox: list[list[float]],
) -> tuple[float, float] | None:
    """Return the center point of an OCR bounding box."""

    if len(bbox) != 4:
        return None

    xs = [point[0] for point in bbox]
    ys = [point[1] for point in bbox]

    return (
        (min(xs) + max(xs)) / 2,
        (min(ys) + max(ys)) / 2,
    )


def _in_zone(
    line: dict[str, Any],
    zone: dict[str, float],
    image_width: int,
    image_height: int,
) -> bool:
    """Check whether an OCR line lies inside a normalized zone."""

    bbox = line.get("bbox", [])

    center = _bbox_center(bbox)

    if center is None:
        return False

    center_x, center_y = center

    zone_x = zone.get("x", 0.0) * image_width
    zone_y = zone.get("y", 0.0) * image_height

    zone_width = zone.get("width", 1.0) * image_width
    zone_height = zone.get("height", 1.0) * image_height

    return (
        zone_x <= center_x <= zone_x + zone_width
        and zone_y <= center_y <= zone_y + zone_height
    )

def _find_value_in_zone(
    lines: list[dict[str, Any]],
    zone: dict[str, float],
    image_width: int,
    image_height: int,
) -> str:
    """Find OCR text located inside a normalized layout zone."""

    matches = []

    for line in lines:
        if _in_zone(
            line,
            zone,
            image_width,
            image_height,
        ):
            text = _clean_line(line.get("text", ""))

            if text:
                matches.append(text)

    return " ".join(matches)


def _find_labeled_value(
    lines: list[dict[str, Any]],
    labels: list[str],
) -> str:
    """Find text appearing after a recognized field label."""

    if not labels:
        return ""

    label_pattern = "|".join(
        re.escape(label)
        for label in labels
    )

    pattern = re.compile(
        rf"(?:{label_pattern})\s*[:\-]?\s*(.+)",
        re.IGNORECASE,
    )

    for line in lines:
        text = _clean_line(line.get("text", ""))

        match = pattern.search(text)

        if match:
            return match.group(1).strip()

    return ""


def map_fields(
    ocr_lines: list[dict[str, Any]],
    document_type: str = "passport",
    image_width: int | None = None,
    image_height: int | None = None,
) -> dict[str, str]:
    """
    Map OCR lines to semantic document fields using the
    configured document layout template.
    """

    template = load_template(document_type)

    if not template:
        return {}

    configured_fields = template.get("fields", {})
    use_spatial_mapping = (
        image_width is not None
        and image_height is not None
        and template.get("coordinate_system") == "normalized"
    )

    fields: dict[str, str] = {}

    # ---------------------------------------------------------
    # Document number
    # ---------------------------------------------------------

        # ---------------------------------------------------------
    # Document number
    # ---------------------------------------------------------

    config = configured_fields.get("document_number", {})

    value = _find_labeled_value(
        ocr_lines,
        config.get("labels", []),
    )

    if not value and use_spatial_mapping:
        value = _find_value_in_zone(
            ocr_lines,
            config.get("zone", {}),
            image_width,
            image_height,
        )

    if value:
        match = DOCUMENT_NUMBER_PATTERN.search(value.upper())

        if match:
            fields["document_number"] = normalize_document_number(
                match.group(0)
            )

    # ---------------------------------------------------------
    # Date of birth
    # ---------------------------------------------------------

        config = configured_fields.get("date_of_birth", {})

    value = _find_labeled_value(
        ocr_lines,
        config.get("labels", []),
    )

    if not value and use_spatial_mapping:
        value = _find_value_in_zone(
            ocr_lines,
            config.get("zone", {}),
            image_width,
            image_height,
        )

    if value:
        match = DATE_PATTERN.search(value)

        if match:
            fields["date_of_birth"] = normalize_date(
                match.group(0)
            )

    # ---------------------------------------------------------
    # Date of expiry
    # ---------------------------------------------------------

        config = configured_fields.get("date_of_expiry", {})

    value = _find_labeled_value(
        ocr_lines,
        config.get("labels", []),
    )

    if not value and use_spatial_mapping:
        value = _find_value_in_zone(
            ocr_lines,
            config.get("zone", {}),
            image_width,
            image_height,
        )

    if value:
        match = DATE_PATTERN.search(value)

        if match:
            fields["date_of_expiry"] = normalize_date(
                match.group(0)
            )

    # ---------------------------------------------------------
    # Nationality
    # ---------------------------------------------------------

        config = configured_fields.get("nationality", {})

    value = _find_labeled_value(
        ocr_lines,
        config.get("labels", []),
    )

    if not value and use_spatial_mapping:
        value = _find_value_in_zone(
            ocr_lines,
            config.get("zone", {}),
            image_width,
            image_height,
        )

    if value:
        country = value.split()[0]
        fields["nationality"] = normalize_country(country)

    # ---------------------------------------------------------
    # Surname
    # ---------------------------------------------------------

        config = configured_fields.get("surname", {})

    value = _find_labeled_value(
        ocr_lines,
        config.get("labels", []),
    )

    if not value and use_spatial_mapping:
        value = _find_value_in_zone(
            ocr_lines,
            config.get("zone", {}),
            image_width,
            image_height,
        )

    if value:
        fields["surname"] = normalize_name(value)

    # ---------------------------------------------------------
    # Given names
    # ---------------------------------------------------------

        config = configured_fields.get("given_names", {})

    value = _find_labeled_value(
        ocr_lines,
        config.get("labels", []),
    )

    if not value and use_spatial_mapping:
        value = _find_value_in_zone(
            ocr_lines,
            config.get("zone", {}),
            image_width,
            image_height,
        )

    if value:
        fields["given_names"] = normalize_name(value)

    # ---------------------------------------------------------
    # Combined name
    # ---------------------------------------------------------

    if "surname" in fields or "given_names" in fields:
        fields["name"] = " ".join(
            part
            for part in (
                fields.get("surname", ""),
                fields.get("given_names", ""),
            )
            if part
        )

    return fields