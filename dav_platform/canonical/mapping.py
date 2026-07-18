"""Column mapping engine.

Maps physical column names to canonical business names.
Uses candidate mappings from Detection with confidence scores.
"""

from typing import Dict, List, Optional

from dav_platform.core.contracts import (
    CandidateMapping,
    ColumnMapping,
    DiscoveryResult,
    CANONICAL_COLUMNS,
)


# Canonical roles that map to canonical column names
ROLE_TO_CANONICAL: Dict[str, str] = {
    "store": "store",
    "upc": "upc",
    "description": "description",
    "brand": "brand",
    "department": "department",
    "category": "category",
    "units": "quantity",
    "weighted_qty": "quantity",
    "price": "price",
    "sales": "price",
    "currency": "uom",
    "date": "date",
    "time": "date",
    "promotion": "category",
    "store_type": "store",
    "region": "store",
    "division": "department",
    "uom": "uom",
    "record_type": "store",
}

# Candidate field name to role mapping
CANDIDATE_FIELD_TO_ROLE: Dict[str, str] = {
    "candidate_store": "store",
    "candidate_upc": "upc",
    "candidate_description": "description",
    "candidate_brand": "brand",
    "candidate_department": "department",
    "candidate_category": "category",
    "candidate_units": "units",
    "candidate_weighted_qty": "weighted_qty",
    "candidate_price": "price",
    "candidate_sales": "sales",
    "candidate_currency": "currency",
    "candidate_date": "date",
    "candidate_time": "time",
    "candidate_promotion": "promotion",
    "candidate_store_type": "store_type",
    "candidate_region": "region",
    "candidate_division": "division",
    "candidate_uom": "uom",
    "candidate_record_type": "record_type",
}


def map_columns(result: DiscoveryResult) -> List[ColumnMapping]:
    """Map physical columns to canonical names using candidate mappings.

    Priority:
    1. Highest confidence candidate per canonical role
    2. First match wins for each physical column
    """
    mappings: List[ColumnMapping] = []
    mapped_physicals: set = set()
    mapped_canonicals: set = set()

    # Collect all candidates with their roles
    all_candidates: List[tuple] = []  # (role, canonical, CandidateMapping)

    for field_name, role in CANDIDATE_FIELD_TO_ROLE.items():
        candidates = getattr(result, field_name, [])
        canonical = ROLE_TO_CANONICAL.get(role)
        if canonical and candidates:
            for c in candidates:
                all_candidates.append((role, canonical, c))

    # Sort by confidence descending
    all_candidates.sort(key=lambda x: x[2].confidence, reverse=True)

    # Map: each canonical column gets the best candidate
    for role, canonical, candidate in all_candidates:
        if canonical in mapped_canonicals:
            continue  # Already mapped this canonical column
        if candidate.physical_column in mapped_physicals:
            continue  # Already mapped this physical column

        mappings.append(ColumnMapping(
            physical_column=candidate.physical_column,
            canonical_name=canonical,
            confidence=candidate.confidence,
            source="candidate",
        ))
        mapped_physicals.add(candidate.physical_column)
        mapped_canonicals.add(canonical)

    return mappings


def get_mapping_dict(mappings: List[ColumnMapping]) -> Dict[str, str]:
    """Convert mappings to physical_to_canonical dict."""
    return {m.physical_column: m.canonical_name for m in mappings}


def get_canonical_columns(mappings: List[ColumnMapping]) -> List[str]:
    """Get ordered list of canonical column names from mappings."""
    seen = set()
    result = []
    for m in mappings:
        if m.canonical_name not in seen:
            result.append(m.canonical_name)
            seen.add(m.canonical_name)
    return result


def get_unmapped_columns(
    result: DiscoveryResult,
    mappings: List[ColumnMapping],
) -> List[str]:
    """Get physical columns that weren't mapped to any canonical name."""
    mapped = {m.physical_column for m in mappings}
    if result.columns:
        return [col for col in result.columns if col not in mapped]
    return []
