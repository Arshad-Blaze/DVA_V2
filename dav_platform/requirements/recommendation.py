"""Recommendation Engine.

Recommends the best workflow, mode, and strategy based on dataset analysis.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from dav_platform.core.contracts import (
    BusinessGoal,
    CapabilityMatrix,
    CanonicalDataset,
    ProcessingMode,
)
from dav_platform.requirements.mode_selector import GROUPABLE_COLUMNS


@dataclass
class Recommendation:
    """A processing recommendation."""
    best_mode: ProcessingMode = ProcessingMode.RAW_REVIEW
    best_workflow: str = "review"
    aggregation_strategy: str = ""
    calculation_strategy: str = ""
    warnings: List[str] = field(default_factory=list)
    missing_prerequisites: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    confidence: float = 0.0


def recommend(
    dataset: Optional[CanonicalDataset] = None,
    capabilities: Optional[CapabilityMatrix] = None,
    goal: Optional[BusinessGoal] = None,
) -> Recommendation:
    """Generate processing recommendations.

    Args:
        dataset: CanonicalDataset from Canonical Layer
        capabilities: Detected capability matrix
        goal: Detected business goal

    Returns:
        Recommendation with best mode, workflow, strategies
    """
    rec = Recommendation()

    if dataset is None:
        rec.warnings.append("No dataset provided")
        return rec

    cols = set(dataset.canonical_columns) if dataset.canonical_columns else set()
    has_data = dataset.dataframe is not None and not dataset.dataframe.is_empty()
    has_quantity = (
        dataset.metadata is not None
        and dataset.metadata.quantity_column is not None
        and dataset.metadata.quantity_type != "none"
    )
    has_groupable = bool(cols & GROUPABLE_COLUMNS)

    # Determine best mode
    if has_data and has_groupable and has_quantity:
        rec.best_mode = ProcessingMode.AGGREGATE_AND_CALCULATE
    elif has_data and has_groupable:
        rec.best_mode = ProcessingMode.AGGREGATE_ONLY
    else:
        rec.best_mode = ProcessingMode.RAW_REVIEW

    # Determine workflow
    rec.best_workflow = _determine_workflow(goal, rec.best_mode)

    # Determine strategies
    if has_groupable:
        groupable_cols = sorted(cols & GROUPABLE_COLUMNS)
        rec.aggregation_strategy = f"group_by: {', '.join(groupable_cols)}"

    if has_quantity:
        qty_col = dataset.metadata.quantity_column
        rec.calculation_strategy = f"sum({qty_col})"

    # Expected outputs
    if rec.best_mode == ProcessingMode.AGGREGATE_AND_CALCULATE:
        rec.expected_outputs = ["aggregated_dataset", "summary_statistics", "report"]
    elif rec.best_mode == ProcessingMode.AGGREGATE_ONLY:
        rec.expected_outputs = ["aggregated_dataset", "summary"]
    else:
        rec.expected_outputs = ["review_dataset"]

    # Warnings
    if not has_data:
        rec.warnings.append("Dataset has no data rows")
        rec.missing_prerequisites.append("data_rows")

    if not has_groupable:
        rec.warnings.append("No groupable columns found")
        rec.missing_prerequisites.append("groupable_columns")

    if not has_quantity:
        rec.warnings.append("No quantity column found — calculations unavailable")

    # Confidence
    score = 0.0
    if has_data:
        score += 0.3
    if has_groupable:
        score += 0.3
    if has_quantity:
        score += 0.3
    if goal is not None:
        score += 0.1
    rec.confidence = min(score, 1.0)

    return rec


def _determine_workflow(
    goal: Optional[BusinessGoal],
    mode: ProcessingMode,
) -> str:
    """Determine the recommended workflow."""
    if goal == BusinessGoal.VALIDATION:
        return "validate"
    if goal == BusinessGoal.MIGRATION:
        return "migrate"
    if goal == BusinessGoal.COMPARISON:
        return "compare"
    if goal == BusinessGoal.REPORTING:
        return "report"

    if mode == ProcessingMode.AGGREGATE_AND_CALCULATE:
        return "aggregate_calculate_report"
    if mode == ProcessingMode.AGGREGATE_ONLY:
        return "aggregate_report"
    return "review"
