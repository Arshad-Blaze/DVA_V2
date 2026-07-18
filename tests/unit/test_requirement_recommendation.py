"""Tests for recommendation engine."""

import pytest

import polars as pl

from dav_platform.core.contracts import (
    BusinessGoal,
    CanonicalDataset,
    CanonicalMetadata,
    CapabilityMatrix,
    ProcessingMode,
)
from dav_platform.requirements.recommendation import recommend, Recommendation


def _make_dataset(columns=None, has_quantity=True, has_data=True):
    if columns is None:
        columns = ["store", "upc", "quantity"] if has_quantity else ["store", "upc"]
    metadata = CanonicalMetadata(
        total_rows=10 if has_data else 0,
        quantity_column="quantity" if has_quantity else None,
        quantity_type="unit" if has_quantity else "none",
    )
    df = None
    if has_data:
        df = pl.DataFrame({c: ["val"] for c in columns})
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=columns,
        metadata=metadata,
        dataframe=df,
    )


class TestRecommend:
    def test_none_dataset(self):
        rec = recommend(None)
        assert rec.best_mode == ProcessingMode.RAW_REVIEW
        assert len(rec.warnings) > 0

    def test_full_dataset(self):
        rec = recommend(_make_dataset())
        assert rec.best_mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert rec.best_workflow == "aggregate_calculate_report"
        assert rec.confidence > 0.8
        assert "aggregated_dataset" in rec.expected_outputs

    def test_groupable_no_quantity(self):
        rec = recommend(_make_dataset(columns=["store", "upc"], has_quantity=False))
        assert rec.best_mode == ProcessingMode.AGGREGATE_ONLY
        assert rec.best_workflow == "aggregate_report"

    def test_no_groupable(self):
        rec = recommend(_make_dataset(columns=["upc", "description"], has_quantity=False))
        assert rec.best_mode == ProcessingMode.RAW_REVIEW
        assert rec.best_workflow == "review"

    def test_aggregation_strategy(self):
        rec = recommend(_make_dataset())
        assert "store" in rec.aggregation_strategy or "store" in rec.aggregation_strategy

    def test_calculation_strategy(self):
        rec = recommend(_make_dataset())
        assert "quantity" in rec.calculation_strategy

    def test_goal_validation(self):
        rec = recommend(_make_dataset(), goal=BusinessGoal.VALIDATION)
        assert rec.best_workflow == "validate"

    def test_goal_migration(self):
        rec = recommend(_make_dataset(), goal=BusinessGoal.MIGRATION)
        assert rec.best_workflow == "migrate"

    def test_goal_comparison(self):
        rec = recommend(_make_dataset(), goal=BusinessGoal.COMPARISON)
        assert rec.best_workflow == "compare"

    def test_no_data_warnings(self):
        rec = recommend(_make_dataset(has_data=False))
        assert "data_rows" in rec.missing_prerequisites

    def test_confidence_score(self):
        rec = recommend(_make_dataset())
        assert 0.0 <= rec.confidence <= 1.0
