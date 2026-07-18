"""Mode validation for the Requirement Layer.

Validates that the selected processing mode is compatible with the canonical data.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from dav_platform.core.contracts import CanonicalDataset, ProcessingMode
from dav_platform.requirements.mode_selector import GROUPABLE_COLUMNS


@dataclass
class ModeValidationResult:
    """Result of mode validation."""
    passed: bool = True
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_mode(
    mode: ProcessingMode,
    dataset: Optional[CanonicalDataset],
) -> ModeValidationResult:
    """Validate that the selected mode is compatible with the dataset.

    Args:
        mode: Requested processing mode
        dataset: CanonicalDataset from Canonical Layer

    Returns:
        ModeValidationResult with pass/fail and any issues
    """
    result = ModeValidationResult()

    if dataset is None:
        result.passed = False
        result.issues.append("No dataset provided")
        return result

    # Check if data exists
    has_data = dataset.dataframe is not None and not dataset.dataframe.is_empty()
    if not has_data:
        result.warnings.append("Dataset has no data rows")

    # Mode-specific validation
    if mode == ProcessingMode.RAW_REVIEW:
        _validate_raw_review(dataset, result, has_data)
    elif mode == ProcessingMode.AGGREGATE_ONLY:
        _validate_aggregate_only(dataset, result, has_data)
    elif mode == ProcessingMode.AGGREGATE_AND_CALCULATE:
        _validate_aggregate_and_calculate(dataset, result, has_data)

    return result


def check_data_readiness(dataset: Optional[CanonicalDataset]) -> List[str]:
    """Check if canonical data is ready for processing.

    Returns a list of readiness issues (empty if ready).

    Args:
        dataset: CanonicalDataset from Canonical Layer

    Returns:
        List of issue strings (empty if data is ready)
    """
    issues = []

    if dataset is None:
        issues.append("No dataset provided")
        return issues

    if not dataset.canonical_columns:
        issues.append("No canonical columns defined")

    if dataset.metadata is None:
        issues.append("No metadata available")

    if dataset.dataframe is None:
        issues.append("No dataframe available")
    elif dataset.dataframe.is_empty():
        issues.append("Dataframe is empty")

    return issues


def _validate_raw_review(
    dataset: CanonicalDataset,
    result: ModeValidationResult,
    has_data: bool,
) -> None:
    """Validate RAW_REVIEW mode."""
    if not has_data:
        result.passed = False
        result.issues.append("RAW_REVIEW requires data rows")


def _validate_aggregate_only(
    dataset: CanonicalDataset,
    result: ModeValidationResult,
    has_data: bool,
) -> None:
    """Validate AGGREGATE_ONLY mode."""
    if not has_data:
        result.passed = False
        result.issues.append("AGGREGATE_ONLY requires data rows")

    # Check for groupable columns
    groupable = [c for c in dataset.canonical_columns if c in GROUPABLE_COLUMNS]
    if not groupable:
        result.passed = False
        result.issues.append(
            f"AGGREGATE_ONLY requires at least one groupable column "
            f"({', '.join(sorted(GROUPABLE_COLUMNS))})"
        )


def _validate_aggregate_and_calculate(
    dataset: CanonicalDataset,
    result: ModeValidationResult,
    has_data: bool,
) -> None:
    """Validate AGGREGATE_AND_CALCULATE mode."""
    if not has_data:
        result.passed = False
        result.issues.append("AGGREGATE_AND_CALCULATE requires data rows")

    # Check for groupable columns
    groupable = [c for c in dataset.canonical_columns if c in GROUPABLE_COLUMNS]
    if not groupable:
        result.passed = False
        result.issues.append(
            f"AGGREGATE_AND_CALCULATE requires at least one groupable column "
            f"({', '.join(sorted(GROUPABLE_COLUMNS))})"
        )

    # Check for quantity column
    has_quantity = (
        dataset.metadata is not None
        and dataset.metadata.quantity_column is not None
        and dataset.metadata.quantity_type != "none"
    )
    if not has_quantity:
        result.passed = False
        result.issues.append("AGGREGATE_AND_CALCULATE requires a quantity column")
