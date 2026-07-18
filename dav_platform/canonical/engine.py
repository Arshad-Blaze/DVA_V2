"""Canonical Engine — Main orchestrator for business data standardization.

Consumes DiscoveryResult and produces CanonicalDataset.
Runs exactly once per file after Detection.
"""

from typing import List, Optional

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ColumnMapping,
    DiscoveryResult,
    FileType,
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
from dav_platform.canonical.schema import build_business_schema, get_schema_info
from dav_platform.canonical.validation import validate_canonical, ValidationResult
from dav_platform.canonical.preview import generate_canonical_preview


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

    def __init__(self):
        pass

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

        # Build schema info
        schema_info = get_schema_info(result, mappings)

        # Build metadata
        metadata = CanonicalMetadata(
            total_rows=data.height if data is not None else 0,
            mapped_columns=len(mappings),
            unmapped_columns=len(unmapped),
            quantity_column=qty_col,
            quantity_type=qty_type,
            confidence=result.confidence,
            source_file_type=result.file_type.value,
            encoding=result.encoding,
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
        if not validation.passed:
            warnings.extend(validation.issues)
        warnings.extend(validation.warnings)

        return dataset

    def transform_streaming(
        self,
        result: DiscoveryResult,
        source,
        chunk_size: int = 1000,
    ):
        """Stream canonical transformation in chunks.

        For large files, processes data in chunks to avoid memory issues.
        """
        from dav_platform.canonical.streaming import stream_canonical_rows
        return stream_canonical_rows(result, source, chunk_size)
