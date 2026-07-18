"""Mode selection for the Requirement Layer.

Handles user selection and availability of processing modes.
"""

from typing import List, Optional

from dav_platform.core.contracts import CanonicalDataset, ProcessingMode


# Columns that can be used for aggregation
GROUPABLE_COLUMNS = {"store", "brand", "category", "department", "date", "region", "division"}


def get_available_modes(dataset: Optional[CanonicalDataset]) -> List[ProcessingMode]:
    """Get processing modes available for this dataset.

    Args:
        dataset: CanonicalDataset from the Canonical Layer

    Returns:
        List of available ProcessingMode values
    """
    if dataset is None:
        return [ProcessingMode.RAW_REVIEW]

    available = [ProcessingMode.RAW_REVIEW]

    # Check for groupable columns
    has_groupable = False
    if dataset.canonical_columns:
        has_groupable = any(c in GROUPABLE_COLUMNS for c in dataset.canonical_columns)

    if has_groupable:
        available.append(ProcessingMode.AGGREGATE_ONLY)

        # Aggregate + Calculate also needs quantity
        has_quantity = (
            dataset.metadata is not None
            and dataset.metadata.quantity_column is not None
            and dataset.metadata.quantity_type != "none"
        )
        if has_quantity:
            available.append(ProcessingMode.AGGREGATE_AND_CALCULATE)

    return available


def suggest_mode(dataset: Optional[CanonicalDataset]) -> ProcessingMode:
    """Suggest the best processing mode for this dataset.

    Selection priority:
    1. AGGREGATE_AND_CALCULATE (if data supports it)
    2. AGGREGATE_ONLY (if data supports it)
    3. RAW_REVIEW (always available)

    Args:
        dataset: CanonicalDataset from the Canonical Layer

    Returns:
        Suggested ProcessingMode
    """
    available = get_available_modes(dataset)

    if ProcessingMode.AGGREGATE_AND_CALCULATE in available:
        return ProcessingMode.AGGREGATE_AND_CALCULATE
    if ProcessingMode.AGGREGATE_ONLY in available:
        return ProcessingMode.AGGREGATE_ONLY
    return ProcessingMode.RAW_REVIEW


def select_mode(
    mode: ProcessingMode,
    dataset: Optional[CanonicalDataset] = None,
) -> ProcessingMode:
    """Select a processing mode.

    Validates that the requested mode is available for the given dataset.
    Falls back to RAW_REVIEW if the mode is not available.

    Args:
        mode: Requested processing mode
        dataset: CanonicalDataset (for availability check)

    Returns:
        Selected ProcessingMode (may differ from requested if unavailable)
    """
    if dataset is None:
        if mode == ProcessingMode.RAW_REVIEW:
            return mode
        return ProcessingMode.RAW_REVIEW

    available = get_available_modes(dataset)
    if mode in available:
        return mode

    return ProcessingMode.RAW_REVIEW
