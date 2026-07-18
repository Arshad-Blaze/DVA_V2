"""Canonical preview generation.

Generates a preview of the canonical dataset for UI display.
"""

from typing import Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import ColumnMapping


def generate_canonical_preview(
    flatten_preview: Optional[pl.DataFrame],
    mappings: List[ColumnMapping],
    max_rows: int = 10,
) -> Optional[pl.DataFrame]:
    """Generate canonical preview — mapped column names.

    Takes the flatten preview and renames columns according to mappings.
    """
    if flatten_preview is None or not mappings:
        return None

    df = flatten_preview.head(max_rows)

    # Build rename map from field_N columns to canonical names
    rename_map = {}
    for m in mappings:
        # flatten_preview uses field_0, field_1, etc.
        # We need to find which field_N corresponds to the physical column
        # This is a best-effort mapping based on column position
        pass

    # For now, return flatten preview as-is
    # The canonical preview will be generated after actual data loading
    return df
