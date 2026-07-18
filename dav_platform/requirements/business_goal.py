"""Business Goal Analysis.

Determines the intended business objective from user intent and dataset characteristics.
"""

from typing import Optional

from dav_platform.core.contracts import BusinessGoal, CanonicalDataset, ProcessingMode


# Mapping from processing mode to likely business goal
MODE_TO_GOAL = {
    ProcessingMode.RAW_REVIEW: BusinessGoal.RAW_REVIEW,
    ProcessingMode.AGGREGATE_ONLY: BusinessGoal.AGGREGATION,
    ProcessingMode.AGGREGATE_AND_CALCULATE: BusinessGoal.CALCULATION,
}


def detect_business_goal(
    dataset: Optional[CanonicalDataset] = None,
    mode: Optional[ProcessingMode] = None,
    options: Optional[dict] = None,
) -> BusinessGoal:
    """Detect the business goal from available information.

    Priority:
    1. Explicit goal in options
    2. Goal inferred from processing mode
    3. Goal inferred from dataset characteristics

    Args:
        dataset: CanonicalDataset from Canonical Layer
        mode: Selected processing mode
        options: User-specified options (may contain 'business_goal')

    Returns:
        Detected BusinessGoal
    """
    options = options or {}

    # 1. Explicit goal in options
    if "business_goal" in options:
        goal_str = options["business_goal"]
        for g in BusinessGoal:
            if g.value == goal_str:
                return g

    # 2. Inferred from mode
    if mode and mode in MODE_TO_GOAL:
        return MODE_TO_GOAL[mode]

    # 3. Inferred from dataset
    if dataset is not None:
        return _infer_goal_from_dataset(dataset)

    return BusinessGoal.RAW_REVIEW


def _infer_goal_from_dataset(dataset: CanonicalDataset) -> BusinessGoal:
    """Infer business goal from dataset characteristics."""
    if dataset.metadata is None:
        return BusinessGoal.RAW_REVIEW

    has_quantity = (
        dataset.metadata.quantity_column is not None
        and dataset.metadata.quantity_type != "none"
    )

    if has_quantity:
        return BusinessGoal.AGGREGATION

    return BusinessGoal.RAW_REVIEW
