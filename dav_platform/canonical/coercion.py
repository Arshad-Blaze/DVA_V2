"""Type coercion for canonical columns.

Converts string values to appropriate types.
"""

from typing import Any, Optional

import polars as pl


def coerce_numeric(value: Any) -> Optional[float]:
    """Convert value to numeric, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def coerce_integer(value: Any) -> Optional[int]:
    """Convert value to integer, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def coerce_date(value: Any) -> Optional[str]:
    """Convert value to date string (YYYY-MM-DD), returning None on failure."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None

    # Try common date formats
    from datetime import datetime
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y%m%d",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%m/%d/%y",
        "%d/%m/%y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


# Canonical column to coercion function
COERCION_MAP = {
    "store": coerce_integer,
    "upc": str,
    "description": str,
    "quantity": coerce_numeric,
    "weight": coerce_numeric,
    "price": coerce_numeric,
    "category": str,
    "brand": str,
    "department": str,
    "date": coerce_date,
    "uom": str,
}


def coerce_column(
    df: pl.DataFrame,
    physical_col: str,
    canonical_name: str,
) -> pl.DataFrame:
    """Coerce a column to its canonical type."""
    if physical_col not in df.columns:
        return df

    func = COERCION_MAP.get(canonical_name)
    if func is None or func is str:
        return df

    if func == coerce_numeric:
        return df.with_columns(
            pl.col(physical_col).cast(pl.Float64, strict=False).alias(physical_col)
        )
    elif func == coerce_integer:
        return df.with_columns(
            pl.col(physical_col).cast(pl.Int64, strict=False).alias(physical_col)
        )
    elif func == coerce_date:
        # Keep as string for now; date parsing is complex in Polars
        return df

    return df
