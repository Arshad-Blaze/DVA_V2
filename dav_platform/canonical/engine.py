"""Canonical Engine — Main orchestrator for business data standardization.

Consumes DiscoveryResult and produces CanonicalDataset.
Runs exactly once per file after Detection.
"""

from typing import Generator, Optional

import polars as pl

from dav_platform.core.contracts import (
    CANONICAL_COLUMNS,
    CanonicalDataset,
    CanonicalMetadata,
    DiscoveryResult,
)
from dav_platform.canonical.mapping import (
    get_canonical_columns,
    get_mapping_dict,
    get_unmapped_columns,
    map_columns,
)
from dav_platform.canonical.quantity import resolve_quantity
from dav_platform.canonical.quantity_norm import normalize_quantity
from dav_platform.canonical.uom import normalize_uom
from dav_platform.canonical.schema import build_business_schema
from dav_platform.canonical.validation import validate_canonical


class CanonicalEngine:
    """Orchestrates canonical transformation.

    Consumes DiscoveryResult and produces CanonicalDataset.
    Detection is FROZEN — this layer consumes its output.

    This is the ONLY transformation boundary.
    After this layer, no downstream layer knows about:
    - retailer layouts
    - physical columns
    - fixed width
    - multiline records
    - record hierarchies
    - delimiters
    """

    def transform(
        self,
        result: DiscoveryResult,
        data: Optional[pl.DataFrame] = None,
    ) -> CanonicalDataset:
        """Transform DiscoveryResult into CanonicalDataset.

        Args:
            result: Output from Detection Layer (frozen)
            data: Optional pre-loaded data (for testing/integration)

        Returns:
            CanonicalDataset with mapped columns and metadata
        """
        # Map physical columns to canonical names
        mappings = map_columns(result)
        mapping_dict = get_mapping_dict(mappings)
        canonical_cols = get_canonical_columns(mappings)
        unmapped = get_unmapped_columns(result, mappings)

        # Build business schema
        business_schema = build_business_schema(mappings)

        # Resolve quantity
        qty_col, qty_type = resolve_quantity(result)

        # Normalize quantity if data available
        if data is not None and not data.is_empty():
            data, qty_col_norm, qty_type_norm = normalize_quantity(data, result)
            if qty_type_norm != "none":
                qty_col = qty_col_norm
                qty_type = qty_type_norm

            # Normalize UOM
            data = normalize_uom(data, result)

        # Resolve quantity_column to canonical name (isolation boundary)
        qty_col_canonical = mapping_dict.get(qty_col, qty_col) if qty_col else None

        # Rename DataFrame columns from physical to canonical and drop unmapped columns.
        # Skip renames where the target canonical name already exists
        # (e.g. "quantity" or "uom" created by normalize_quantity/uom).
        if data is not None and not data.is_empty():
            existing_cols = set(data.columns)
            mapped_physicals = {m.physical_column for m in mappings}
            rename_map = {}
            drop_cols = []
            for phys, canon in mapping_dict.items():
                if phys in existing_cols:
                    if canon in existing_cols:
                        drop_cols.append(phys)
                    else:
                        rename_map[phys] = canon
            # Drop unmapped physical columns (not in any mapping and not already canonical)
            canonical_names = set(CANONICAL_COLUMNS.keys())
            for col in existing_cols:
                if col not in mapped_physicals and col not in rename_map and col not in canonical_names:
                    drop_cols.append(col)
            if drop_cols:
                data = data.drop(drop_cols)
            if rename_map:
                data = data.rename(rename_map)

        # Build metadata
        metadata = CanonicalMetadata(
            total_rows=data.height if data is not None else 0,
            mapped_columns=len(mappings),
            unmapped_columns=len(unmapped),
            quantity_column=qty_col_canonical,
            quantity_type=qty_type,
            confidence=result.confidence,
            source_file_type=result.file_type.value,
            encoding=result.encoding,
            flatten_strategy="direct",
            uom_strategy="detected" if qty_col else "default",
            ignored_columns=[],
            warnings=list(result.warnings),
            transformation_log=[
                f"mapped {len(mappings)} columns",
                f"quantity type: {qty_type}",
                f"business schema: {len(business_schema)} columns",
            ],
        )

        # Build warnings
        warnings = list(result.warnings)
        if unmapped:
            warnings.append(f"Unmapped columns: {', '.join(unmapped)}")

        # Build recommendations
        recommendations = list(result.recommendations)
        if not mappings:
            recommendations.append("No column mappings found — manual mapping may be required")

        # Create dataset
        dataset = CanonicalDataset(
            file_path=result.file_path,
            physical_to_canonical=mapping_dict,
            canonical_columns=canonical_cols,
            column_mappings=mappings,
            dataframe=data,
            metadata=metadata,
            warnings=warnings,
            recommendations=recommendations,
        )

        # Validate
        validation = validate_canonical(dataset)
        metadata.validation_summary = {
            "passed": validation.passed,
            "issues": validation.issues,
            "warnings": validation.warnings,
            "checked_columns": validation.checked_columns,
            "total_rows": validation.total_rows,
        }
        if not validation.passed:
            warnings.extend(validation.issues)
        warnings.extend(validation.warnings)

        return dataset

    def transform_streaming(
        self,
        chunks: Generator[pl.DataFrame, None, None],
        result: DiscoveryResult,
    ) -> Generator[CanonicalDataset, None, None]:
        """Stream canonical transformation in chunks.

        Receives pre-parsed data chunks and applies canonical transformations.
        Yields CanonicalDataset objects for each chunk.

        Args:
            chunks: Generator of pre-parsed DataFrames
            result: DiscoveryResult from Detection

        Yields:
            CanonicalDataset for each chunk
        """
        for chunk in chunks:
            if chunk is None or chunk.is_empty():
                continue
            yield self.transform(result, data=chunk)
