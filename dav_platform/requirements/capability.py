"""Capability Detection.

Determines what operations the dataset supports.
"""

from typing import Optional

from dav_platform.core import CanonicalDataset, CapabilityMatrix
from dav_platform.requirements.mode_selector import GROUPABLE_COLUMNS


def detect_capabilities(
    dataset: Optional[CanonicalDataset] = None,
) -> CapabilityMatrix:
    """Detect what operations the dataset supports.

    Analyzes the dataset to determine which capabilities are available.

    Args:
        dataset: CanonicalDataset from Canonical Layer

    Returns:
        CapabilityMatrix with boolean flags
    """
    if dataset is None:
        return CapabilityMatrix(can_review=True)

    cols = set(dataset.canonical_columns) if dataset.canonical_columns else set()
    has_data = dataset.dataframe is not None and not dataset.dataframe.is_empty()
    has_quantity = (
        dataset.metadata is not None
        and dataset.metadata.quantity_column is not None
        and dataset.metadata.quantity_type != "none"
    )
    has_groupable = bool(cols & GROUPABLE_COLUMNS)

    return CapabilityMatrix(
        can_review=has_data,
        can_aggregate=has_data and has_groupable,
        can_calculate=has_data and has_groupable and has_quantity,
        can_validate=has_data,
        can_migrate=has_data and len(cols) >= 2,
        can_report=has_data and has_groupable,
        can_compare=False,  # requires a second dataset, checked externally
    )


def get_capability_summary(matrix: CapabilityMatrix) -> str:
    """Get a human-readable summary of capabilities.

    Args:
        matrix: CapabilityMatrix to summarize

    Returns:
        Summary string
    """
    capabilities = [k.replace("can_", "") for k, v in matrix.to_dict().items() if v]
    if not capabilities:
        return "No capabilities available"
    return f"Available: {', '.join(capabilities)}"
