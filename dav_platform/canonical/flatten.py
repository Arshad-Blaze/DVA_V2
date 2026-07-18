"""Record hierarchy flattening.

Combines related records (HDR, S, U, TRL) into single logical business records.
Processing must never know hierarchical records existed.
"""

from typing import Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import RecordTypeInfo


def flatten_hierarchy(
    lines: List[str],
    record_types: List[RecordTypeInfo],
    delimiter: Optional[str] = None,
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Flatten hierarchical records into logical business rows.

    Strategy:
    - Header records provide context (store, date)
    - Detail records are the primary data
    - Summary/trailer records provide totals
    - Each detail row gets header context merged in

    Args:
        lines: Raw file lines
        record_types: Detected record types with prefixes
        delimiter: Field delimiter (for splitting)
        header_prefix: Header record prefix
        trailer_prefix: Trailer record prefix

    Returns:
        List of flattened row dicts
    """
    if not lines or not record_types:
        return []

    # Identify record type prefixes
    header_prefixes = set()
    trailer_prefixes = set()
    detail_prefixes = set()

    for rt in record_types:
        prefix = rt.prefix
        if header_prefix and prefix == header_prefix:
            header_prefixes.add(prefix)
        elif trailer_prefix and prefix == trailer_prefix:
            trailer_prefixes.add(prefix)
        else:
            detail_prefixes.add(prefix)

    # If no clear hierarchy, treat all as detail
    if not header_prefixes and not trailer_prefixes:
        detail_prefixes = {rt.prefix for rt in record_types}

    # Process lines
    current_header: Dict[str, str] = {}
    rows: List[Dict[str, str]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Determine record type
        record_type = "detail"
        matched_prefix = None
        for rt in record_types:
            if stripped.startswith(rt.prefix):
                record_type = rt.prefix
                matched_prefix = rt.prefix
                break

        # Parse fields
        fields = _parse_fields(stripped, delimiter)

        if matched_prefix in header_prefixes:
            # Store header context
            current_header = fields
        elif matched_prefix in trailer_prefixes:
            # Skip trailer (totals are usually recalculated)
            continue
        else:
            # Detail record — merge with header context
            merged = {**current_header, **fields}
            merged["_record_type"] = record_type
            rows.append(merged)

    return rows


def _parse_fields(line: str, delimiter: Optional[str]) -> Dict[str, str]:
    """Parse a line into field dict."""
    if delimiter:
        parts = line.split(delimiter)
        return {f"field_{i}": part.strip() for i, part in enumerate(parts)}
    else:
        return {"content": line}


def hierarchy_to_dataframe(
    lines: List[str],
    record_types: List[RecordTypeInfo],
    delimiter: Optional[str] = None,
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
) -> Optional[pl.DataFrame]:
    """Flatten hierarchy and return as DataFrame."""
    rows = flatten_hierarchy(lines, record_types, delimiter, header_prefix, trailer_prefix)
    if not rows:
        return None
    return pl.DataFrame(rows)
