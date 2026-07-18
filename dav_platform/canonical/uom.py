"""UOM normalization.

Normalizes common unit of measure values to standard format.
"""

from typing import Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import CandidateMapping, DiscoveryResult


# Standard UOM mappings
UOM_MAP: Dict[str, str] = {
    "KG": "KG",
    "KILOGRAM": "KG",
    "KILOGRAMS": "KG",
    "LB": "LB",
    "POUND": "LB",
    "POUNDS": "LB",
    "EA": "EA",
    "EACH": "EA",
    "CT": "CT",
    "COUNT": "CT",
    "G": "G",
    "GRAM": "G",
    "GRAMS": "G",
    "OZ": "OZ",
    "OUNCE": "OZ",
    "OUNCES": "OZ",
    "CS": "CS",
    "CASE": "CS",
    "PACK": "PK",
    "PK": "PK",
    "BAG": "BG",
    "BG": "BG",
}


def normalize_uom(
    df: Optional[pl.DataFrame],
    result: DiscoveryResult,
) -> Optional[pl.DataFrame]:
    """Normalize UOM column in DataFrame.

    Maps common UOM values to standard format using vectorized operations.
    If no UOM column exists, adds one with default "EA".
    """
    if df is None or df.is_empty():
        return df

    # Find UOM column
    uom_col = None
    for c in result.candidate_uom:
        if c.physical_column in df.columns:
            uom_col = c.physical_column
            break

    if uom_col:
        # Normalize using vectorized replace (stays in Rust kernel)
        df = df.with_columns(
            pl.col(uom_col)
            .str.to_uppercase()
            .str.strip_chars()
            .replace_strict(UOM_MAP, default="EA")
            .alias("uom")
        )
    else:
        # Add default UOM column
        df = df.with_columns(pl.lit("EA").alias("uom"))

    return df
