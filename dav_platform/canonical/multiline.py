"""Multiline flattening.

Combines records spanning multiple physical lines into single canonical rows.
Example:
    U|12345|Product
    Continuation line 1
    Continuation line 2
→
    One canonical row with all data combined.
"""

from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import RecordTypeInfo


def flatten_multiline(
    lines: List[str],
    delimiter: Optional[str] = None,
    record_types: Optional[List[RecordTypeInfo]] = None,
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Flatten multiline records into single-row dicts.

    Continuation lines (no prefix) are appended to the previous record's
    last field or stored as _continuation.

    Args:
        lines: Raw file lines
        delimiter: Field delimiter
        record_types: Known record types (to identify primary vs continuation)
        header_prefix: Header prefix (skipped)
        trailer_prefix: Trailer prefix (skipped)

    Returns:
        List of flattened row dicts
    """
    if not lines:
        return []

    # Build set of known prefixes
    known_prefixes = set()
    if record_types:
        for rt in record_types:
            known_prefixes.add(rt.prefix)
    if header_prefix:
        known_prefixes.add(header_prefix)
    if trailer_prefix:
        known_prefixes.add(trailer_prefix)

    rows: List[Dict[str, Any]] = []
    current_row: Optional[Dict[str, Any]] = None
    current_fields: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if this line starts with a known prefix
        is_primary = any(stripped.startswith(prefix) for prefix in known_prefixes)

        if is_primary:
            # Save previous row if exists
            if current_row is not None:
                _finalize_row(current_row, current_fields, delimiter)
                rows.append(current_row)

            # Start new row
            current_row = {"_raw": stripped}
            current_fields = _parse_line_fields(stripped, delimiter)
        else:
            # Continuation line — append to current fields
            if current_row is not None:
                continuation_fields = _parse_line_fields(stripped, delimiter)
                current_fields.extend(continuation_fields)

    # Finalize last row
    if current_row is not None:
        _finalize_row(current_row, current_fields, delimiter)
        rows.append(current_row)

    return rows


def _parse_line_fields(line: str, delimiter: Optional[str]) -> List[str]:
    """Parse line into field values."""
    if delimiter:
        return [part.strip() for part in line.split(delimiter)]
    return [line]


def _finalize_row(row: Dict[str, Any], fields: List[str], delimiter: Optional[str]) -> None:
    """Finalize a row with all accumulated fields."""
    for i, value in enumerate(fields):
        row[f"field_{i}"] = value
    row["field_count"] = len(fields)


def multiline_to_dataframe(
    lines: List[str],
    delimiter: Optional[str] = None,
    record_types: Optional[List[RecordTypeInfo]] = None,
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
) -> Optional[pl.DataFrame]:
    """Flatten multiline records and return as DataFrame."""
    rows = flatten_multiline(lines, delimiter, record_types, header_prefix, trailer_prefix)
    if not rows:
        return None
    return pl.DataFrame(rows)
