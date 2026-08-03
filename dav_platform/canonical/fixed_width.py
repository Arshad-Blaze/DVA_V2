"""Fixed-width transformation engine.

Slices fixed-width records into fields using Detection's layout intelligence.
Processing must never perform fixed-width parsing.
"""

from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import LayoutField


def transform_fixed_width(
    lines: List[str],
    layout_fields: List[LayoutField],
    record_types: Optional[List[str]] = None,
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
    data_start_line: int = 0,
) -> List[Dict[str, Any]]:
    """Transform fixed-width lines into row dicts using layout fields.

    Args:
        lines: Raw file lines
        layout_fields: Detected field positions from Detection
        record_types: Known record type prefixes (optional filter)
        header_prefix: Header record prefix (skipped)
        trailer_prefix: Trailer record prefix (skipped)
        data_start_line: Line index where data begins

    Returns:
        List of row dicts with field values trimmed
    """
    rows: List[Dict[str, Any]] = []

    for i, line in enumerate(lines):
        # Skip header/trailer records
        if header_prefix and line.startswith(header_prefix):
            continue
        if trailer_prefix and line.startswith(trailer_prefix):
            continue

        # Skip lines before data start
        if i < data_start_line:
            continue

        row = {"_line_number": i + 1}

        for field in layout_fields:
            start = field.start
            end = start + field.width if field.width > 0 else len(line)
            value = line[start:end].strip() if start < len(line) else ""
            row[field.probable_name or f"field_{start}"] = value

        rows.append(row)

    return rows


def fixed_width_to_dataframe(
    lines: List[str],
    layout_fields: List[LayoutField],
    record_types: Optional[List[str]] = None,
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
    data_start_line: int = 0,
) -> Optional[pl.DataFrame]:
    """Transform fixed-width lines into a Polars DataFrame."""
    rows = transform_fixed_width(
        lines, layout_fields, record_types, header_prefix, trailer_prefix, data_start_line
    )
    if not rows:
        return None
    return pl.DataFrame(rows)


def apply_datatype_conversions(
    df: pl.DataFrame,
    layout_fields: List[LayoutField],
) -> pl.DataFrame:
    """Apply datatype conversions based on LayoutField metadata."""
    if df is None or df.is_empty():
        return df

    for field in layout_fields:
        col_name = field.probable_name or f"field_{field.start}"
        if col_name not in df.columns:
            continue

        if field.datatype == "numeric":
            df = df.with_columns(
                pl.col(col_name).cast(pl.Float64, strict=False).alias(col_name)
            )
        elif field.datatype == "integer":
            df = df.with_columns(
                pl.col(col_name).cast(pl.Int64, strict=False).alias(col_name)
            )

    return df
