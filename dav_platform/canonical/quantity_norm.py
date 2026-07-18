"""Quantity normalization.

Applies business rules to resolve quantity from multiple sources.
Downstream Processing consumes only the canonical Quantity field.
"""

from typing import Optional, Tuple

import polars as pl

from dav_platform.core.contracts import DiscoveryResult


def normalize_quantity(
    df: Optional[pl.DataFrame],
    result: DiscoveryResult,
) -> Tuple[Optional[pl.DataFrame], Optional[str], str]:
    """Normalize quantity column in DataFrame.

    Business rule:
        IF Weight > 0: Quantity = Weight, type = "weight"
        ELIF Units > 0: Quantity = Units, type = "unit"
        ELSE: Quantity = 0, type = "none"

    Args:
        df: Input DataFrame (may be None)
        result: DiscoveryResult with candidate info

    Returns:
        (updated_df, quantity_column_name, quantity_type)
    """
    if df is None or df.is_empty():
        return df, None, "none"

    # Find weight and units columns
    weight_col = _find_column(result.candidate_weighted_qty, df)
    units_col = _find_column(result.candidate_units, df)

    if weight_col and weight_col in df.columns:
        # Try weight first
        df = df.with_columns(
            pl.col(weight_col).cast(pl.Float64, strict=False).alias("_qty_weight")
        )
        has_weight = df["_qty_weight"].drop_nulls().gt(0).any()

        if has_weight:
            df = df.with_columns(pl.col("_qty_weight").alias("quantity"))
            df = df.drop("_qty_weight")
            return df, weight_col, "weight"

        df = df.drop("_qty_weight")

    if units_col and units_col in df.columns:
        # Fallback to units
        df = df.with_columns(
            pl.col(units_col).cast(pl.Float64, strict=False).alias("quantity")
        )
        return df, units_col, "unit"

    # No quantity found
    df = df.with_columns(pl.lit(0.0).alias("quantity"))
    return df, None, "none"


def _find_column(
    candidates,
    df: pl.DataFrame,
) -> Optional[str]:
    """Find first candidate column that exists in DataFrame."""
    for c in candidates:
        if c.physical_column in df.columns:
            return c.physical_column
    return None
