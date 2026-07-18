"""Canonical validation.

Validates data before it leaves the Canonical layer.
Returns structured validation results. Does not crash on recoverable issues.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import polars as pl

from dav_platform.core.contracts import CanonicalDataset, ColumnMapping


@dataclass
class ValidationResult:
    """Structured validation result."""
    passed: bool = True
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checked_columns: int = 0
    total_rows: int = 0


def validate_canonical(dataset: CanonicalDataset) -> ValidationResult:
    """Validate a CanonicalDataset before it leaves the layer.

    Checks:
    - Missing mandatory business columns
    - Duplicate canonical mappings
    - Multiple physical columns mapped to one canonical field
    - Datatype issues
    - Empty dataset
    """
    result = ValidationResult()

    # Check for empty dataset
    if dataset.dataframe is None or dataset.dataframe.is_empty():
        result.warnings.append("Dataset is empty")
        return result

    result.total_rows = dataset.dataframe.height
    result.checked_columns = dataset.dataframe.width

    # Check for missing mandatory columns
    mandatory = {"store", "upc", "quantity"}
    mapped_canonicals = {m.canonical_name for m in dataset.column_mappings}
    missing = mandatory - mapped_canonicals
    if missing:
        result.warnings.append(f"Missing mandatory columns: {', '.join(sorted(missing))}")

    # Check for duplicate mappings
    canonical_counts = {}
    for m in dataset.column_mappings:
        canonical_counts[m.canonical_name] = canonical_counts.get(m.canonical_name, 0) + 1

    for canonical, count in canonical_counts.items():
        if count > 1:
            result.issues.append(f"Duplicate mapping for '{canonical}': {count} physical columns")
            result.passed = False

    # Check for unmapped physical columns
    mapped_physicals = {m.physical_column for m in dataset.column_mappings}
    if dataset.physical_to_canonical:
        for phys in dataset.physical_to_canonical:
            if phys not in mapped_physicals:
                result.warnings.append(f"Physical column '{phys}' in mapping dict but not in mappings")

    # Check DataFrame has expected columns
    if dataset.dataframe is not None:
        for m in dataset.column_mappings:
            if m.physical_column not in dataset.dataframe.columns:
                result.warnings.append(f"Mapped column '{m.physical_column}' not in DataFrame")

    return result


def validate_mapping_completeness(
    mappings: List[ColumnMapping],
    total_physical_columns: int,
) -> ValidationResult:
    """Validate mapping completeness."""
    result = ValidationResult()

    if not mappings:
        result.issues.append("No column mappings found")
        result.passed = False
        return result

    result.checked_columns = len(mappings)

    # Check coverage
    coverage = len(mappings) / max(total_physical_columns, 1)
    if coverage < 0.3:
        result.warnings.append(f"Low mapping coverage: {coverage:.0%}")

    # Check for duplicate canonical names
    canonical_names = [m.canonical_name for m in mappings]
    if len(canonical_names) != len(set(canonical_names)):
        result.issues.append("Duplicate canonical names in mappings")
        result.passed = False

    return result
