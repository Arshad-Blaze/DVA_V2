"""Tests for business goal analysis."""

import pytest

from dav_platform.core.contracts import (
    BusinessGoal,
    CanonicalDataset,
    CanonicalMetadata,
    ProcessingMode,
)
from dav_platform.requirements.business_goal import detect_business_goal


def _make_dataset(has_quantity=True, has_data=True):
    cols = ["store", "upc", "quantity"] if has_quantity else ["store", "upc"]
    metadata = CanonicalMetadata(
        total_rows=10 if has_data else 0,
        quantity_column="quantity" if has_quantity else None,
        quantity_type="unit" if has_quantity else "none",
    )
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=cols,
        metadata=metadata,
    )


class TestDetectBusinessGoal:
    def test_explicit_goal_in_options(self):
        ds = _make_dataset()
        goal = detect_business_goal(ds, options={"business_goal": "migration"})
        assert goal == BusinessGoal.MIGRATION

    def test_inferred_from_aggregate_mode(self):
        ds = _make_dataset()
        goal = detect_business_goal(ds, mode=ProcessingMode.AGGREGATE_ONLY)
        assert goal == BusinessGoal.AGGREGATION

    def test_inferred_from_calculate_mode(self):
        ds = _make_dataset()
        goal = detect_business_goal(ds, mode=ProcessingMode.AGGREGATE_AND_CALCULATE)
        assert goal == BusinessGoal.CALCULATION

    def test_inferred_from_raw_review_mode(self):
        ds = _make_dataset()
        goal = detect_business_goal(ds, mode=ProcessingMode.RAW_REVIEW)
        assert goal == BusinessGoal.RAW_REVIEW

    def test_inferred_from_dataset_with_quantity(self):
        ds = _make_dataset(has_quantity=True)
        goal = detect_business_goal(ds)
        assert goal == BusinessGoal.AGGREGATION

    def test_inferred_from_dataset_without_quantity(self):
        ds = _make_dataset(has_quantity=False)
        goal = detect_business_goal(ds)
        assert goal == BusinessGoal.RAW_REVIEW

    def test_none_dataset(self):
        goal = detect_business_goal(None)
        assert goal == BusinessGoal.RAW_REVIEW

    def test_invalid_goal_string_ignores(self):
        ds = _make_dataset()
        goal = detect_business_goal(ds, options={"business_goal": "nonexistent"})
        assert goal == BusinessGoal.AGGREGATION  # falls through to dataset inference
