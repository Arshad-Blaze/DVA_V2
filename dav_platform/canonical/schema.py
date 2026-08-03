"""Business Schema Builder.

Produces a stable business schema independent of retailer format.
Retailer-specific column names disappear after this layer.
"""

from typing import Any, Dict, List

from dav_platform.core.contracts import (
    ColumnMapping,
    DiscoveryResult,
)


# Standard business schema order
BUSINESS_SCHEMA_ORDER = [
    "store",
    "upc",
    "description",
    "quantity",
    "weight",
    "price",
    "category",
    "brand",
    "department",
    "date",
    "uom",
]


def build_business_schema(
    mappings: List[ColumnMapping],
) -> List[str]:
    """Build ordered business schema from column mappings.

    Returns canonical column names in standard business order,
    including only columns that have mappings.
    """
    mapped_canonicals = {m.canonical_name for m in mappings}
    return [col for col in BUSINESS_SCHEMA_ORDER if col in mapped_canonicals]


def get_schema_info(
    result: DiscoveryResult,
    mappings: List[ColumnMapping],
) -> Dict[str, Any]:
    """Get schema information for metadata.

    Returns dict with schema details:
    - business_columns: ordered list
    - mapped_count: number of mapped columns
    - unmapped_count: number of unmapped physical columns
    - missing_canonicals: canonical columns without mappings
    """
    business_cols = build_business_schema(mappings)
    mapped_canonicals = {m.canonical_name for m in mappings}
    missing = [col for col in BUSINESS_SCHEMA_ORDER if col not in mapped_canonicals]

    return {
        "business_columns": business_cols,
        "mapped_count": str(len(mappings)),
        "unmapped_count": str(len(result.columns) - len(mappings)) if result.columns else "0",
        "missing_canonicals": ",".join(missing) if missing else "none",
    }
