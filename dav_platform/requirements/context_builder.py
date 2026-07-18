"""Context building for the Requirement Layer.

Builds OperationContext from mode + canonical data.
"""

import uuid
from typing import Any, Dict, Optional

import polars as pl

from dav_platform.core.contracts import CanonicalDataset, OperationContext, ProcessingMode


def build_context(
    mode: ProcessingMode,
    dataset: Optional[CanonicalDataset] = None,
    options: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> OperationContext:
    """Build OperationContext from mode and canonical data.

    Args:
        mode: Selected processing mode
        dataset: CanonicalDataset from Canonical Layer
        options: User-specified processing options
        session_id: Optional session ID (generated if not provided)

    Returns:
        OperationContext for the Operation Layer
    """
    if session_id is None:
        session_id = build_session_id()

    metadata = extract_metadata(dataset)

    return OperationContext(
        mode=mode,
        options=options or {},
        session_id=session_id,
        metadata=metadata,
    )


def build_session_id() -> str:
    """Generate a unique session ID.

    Returns:
        UUID-based session identifier
    """
    return str(uuid.uuid4())


def extract_metadata(dataset: Optional[CanonicalDataset]) -> Dict[str, Any]:
    """Extract relevant metadata from canonical dataset.

    Args:
        dataset: CanonicalDataset from Canonical Layer

    Returns:
        Dict of metadata for OperationContext
    """
    if dataset is None:
        return {"has_data": False}

    meta = {
        "file_path": dataset.file_path,
        "total_rows": dataset.metadata.total_rows if dataset.metadata else 0,
        "canonical_columns": list(dataset.canonical_columns),
        "mapped_columns": dataset.metadata.mapped_columns if dataset.metadata else 0,
        "unmapped_columns": dataset.metadata.unmapped_columns if dataset.metadata else 0,
        "quantity_column": dataset.metadata.quantity_column if dataset.metadata else None,
        "quantity_type": dataset.metadata.quantity_type if dataset.metadata else "none",
        "confidence": dataset.metadata.confidence if dataset.metadata else 0.0,
        "source_file_type": dataset.metadata.source_file_type if dataset.metadata else "",
        "encoding": dataset.metadata.encoding if dataset.metadata else "utf-8",
        "flatten_strategy": dataset.metadata.flatten_strategy if dataset.metadata else "none",
        "uom_strategy": dataset.metadata.uom_strategy if dataset.metadata else "none",
        "has_data": dataset.dataframe is not None and not dataset.dataframe.is_empty(),
        "row_count": dataset.dataframe.height if dataset.dataframe is not None else 0,
        "warnings": list(dataset.warnings),
        "recommendations": list(dataset.recommendations),
    }

    return meta
