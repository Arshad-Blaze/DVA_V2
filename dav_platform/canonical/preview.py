"""Canonical preview generation.

Generates a preview of the canonical dataset for UI display.
Only displays business fields — never exposes retailer column names.
"""

from typing import Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import ColumnMapping


def generate_canonical_preview(
    flatten_preview: Optional[pl.DataFrame],
    mappings: List[ColumnMapping],
    max_rows: int = 10,
) -> Optional[pl.DataFrame]:
    """Generate canonical preview — business columns only.

    Takes the flatten preview and renames field_N columns according to mappings.
    Returns only mapped canonical columns — never exposes physical names,
    record types, or internal columns.
    """
    if flatten_preview is None or not mappings:
        return None

    df = flatten_preview.head(max_rows)

    # Build rename map: field_N -> canonical_name
    # Flatten preview uses field_0, field_1, etc. for split columns
    rename_map = {}
    mapped_fields = set()
    for i, m in enumerate(mappings):
        field_name = f"field_{i}"
        if field_name in df.columns:
            rename_map[field_name] = m.canonical_name
            mapped_fields.add(field_name)

    if rename_map:
        df = df.rename(rename_map)

    # Select only the renamed canonical columns to avoid exposing
    # unmapped field_N columns, record types, or other internal columns
    canonical_cols = list(rename_map.values())
    df = df.select(canonical_cols)

    return df
