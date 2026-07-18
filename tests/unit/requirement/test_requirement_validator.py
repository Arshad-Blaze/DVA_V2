"""Tests for requirement validator."""

import pytest

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ProcessingMode,
)
from dav_platform.requirements.validator import (
    ModeValidationResult,
    check_data_readiness,
    validate_mode,
)


def _make_dataset(
    columns=None,
    has_quantity=True,
    has_data=True,
):
    """Helper to create test CanonicalDataset."""
    if columns is None:
        columns = ["store", "upc", "quantity"]

    metadata = CanonicalMetadata(
        total_rows=10 if has_data else 0,
        mapped_columns=len(columns),
        quantity_column="quantity" if has_quantity else None,
        quantity_type="unit" if has_quantity else "none",
    )

    df = None
    if has_data:
        data = {c: ["val"] for c in columns}
        df = pl.DataFrame(data)

    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=columns,
        metadata=metadata,
        dataframe=df,
    )


class TestValidateMode:
    def test_none_dataset(self):
        result = validate_mode(ProcessingMode.RAW_REVIEW, None)
        assert not result.passed
        assert "No dataset provided" in result.issues

    def test_raw_review_with_data(self):
        ds = _make_dataset()
        result = validate_mode(ProcessingMode.RAW_REVIEW, ds)
        assert result.passed

    def test_raw_review_no_data(self):
        ds = _make_dataset(has_data=False)
        result = validate_mode(ProcessingMode.RAW_REVIEW, ds)
        assert not result.passed
        assert any("requires data" in i for i in result.issues)

    def test_aggregate_only_valid(self):
        ds = _make_dataset(columns=["store", "upc"])
        result = validate_mode(ProcessingMode.AGGREGATE_ONLY, ds)
        assert result.passed

    def test_aggregate_only_no_groupable(self):
        ds = _make_dataset(columns=["upc", "description"])
        result = validate_mode(ProcessingMode.AGGREGATE_ONLY, ds)
        assert not result.passed
        assert any("groupable" in i for i in result.issues)

    def test_aggregate_only_no_data(self):
        ds = _make_dataset(columns=["store", "upc"], has_data=False)
        result = validate_mode(ProcessingMode.AGGREGATE_ONLY, ds)
        assert not result.passed

    def test_aggregate_and_calculate_valid(self):
        ds = _make_dataset(columns=["store", "upc", "quantity"], has_quantity=True)
        result = validate_mode(ProcessingMode.AGGREGATE_AND_CALCULATE, ds)
        assert result.passed

    def test_aggregate_and_calculate_no_quantity(self):
        ds = _make_dataset(columns=["store", "upc"], has_quantity=False)
        result = validate_mode(ProcessingMode.AGGREGATE_AND_CALCULATE, ds)
        assert not result.passed
        assert any("quantity" in i for i in result.issues)

    def test_aggregate_and_calculate_no_groupable(self):
        ds = _make_dataset(columns=["upc", "quantity"], has_quantity=True)
        result = validate_mode(ProcessingMode.AGGREGATE_AND_CALCULATE, ds)
        assert not result.passed
        assert any("groupable" in i for i in result.issues)


class TestCheckDataReadiness:
    def test_none_dataset(self):
        issues = check_data_readiness(None)
        assert "No dataset provided" in issues

    def test_ready_dataset(self):
        ds = _make_dataset()
        issues = check_data_readiness(ds)
        assert issues == []

    def test_no_columns(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=[],
            metadata=CanonicalMetadata(),
        )
        issues = check_data_readiness(ds)
        assert any("columns" in i for i in issues)

    def test_no_metadata(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=["store"],
            metadata=None,
        )
        issues = check_data_readiness(ds)
        assert any("metadata" in i for i in issues)

    def test_no_dataframe(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=["store"],
            metadata=CanonicalMetadata(),
            dataframe=None,
        )
        issues = check_data_readiness(ds)
        assert any("dataframe" in i for i in issues)

    def test_empty_dataframe(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=["store"],
            metadata=CanonicalMetadata(),
            dataframe=pl.DataFrame({"store": []}),
        )
        issues = check_data_readiness(ds)
        assert any("empty" in i for i in issues)
