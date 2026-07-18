"""Tests for mode selector."""

import pytest

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ColumnMapping,
    ProcessingMode,
)
from dav_platform.requirements.mode_selector import (
    GROUPABLE_COLUMNS,
    get_available_modes,
    select_mode,
    suggest_mode,
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


class TestGetAvailableModes:
    def test_none_dataset(self):
        modes = get_available_modes(None)
        assert modes == [ProcessingMode.RAW_REVIEW]

    def test_empty_columns(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=[],
            metadata=CanonicalMetadata(),
        )
        modes = get_available_modes(ds)
        assert ProcessingMode.RAW_REVIEW in modes
        assert ProcessingMode.AGGREGATE_ONLY not in modes

    def test_groupable_only(self):
        ds = _make_dataset(columns=["store", "upc"], has_quantity=False)
        modes = get_available_modes(ds)
        assert ProcessingMode.RAW_REVIEW in modes
        assert ProcessingMode.AGGREGATE_ONLY in modes
        assert ProcessingMode.AGGREGATE_AND_CALCULATE not in modes

    def test_groupable_and_quantity(self):
        ds = _make_dataset(columns=["store", "upc", "quantity"], has_quantity=True)
        modes = get_available_modes(ds)
        assert ProcessingMode.RAW_REVIEW in modes
        assert ProcessingMode.AGGREGATE_ONLY in modes
        assert ProcessingMode.AGGREGATE_AND_CALCULATE in modes

    def test_no_groupable_columns(self):
        ds = _make_dataset(columns=["upc", "description"], has_quantity=False)
        modes = get_available_modes(ds)
        assert modes == [ProcessingMode.RAW_REVIEW]

    def test_brand_as_groupable(self):
        ds = _make_dataset(columns=["brand", "upc"], has_quantity=False)
        modes = get_available_modes(ds)
        assert ProcessingMode.AGGREGATE_ONLY in modes

    def test_category_as_groupable(self):
        ds = _make_dataset(columns=["category", "upc"], has_quantity=False)
        modes = get_available_modes(ds)
        assert ProcessingMode.AGGREGATE_ONLY in modes

    def test_department_as_groupable(self):
        ds = _make_dataset(columns=["department", "upc"], has_quantity=False)
        modes = get_available_modes(ds)
        assert ProcessingMode.AGGREGATE_ONLY in modes


class TestSuggestMode:
    def test_none_dataset(self):
        assert suggest_mode(None) == ProcessingMode.RAW_REVIEW

    def test_suggests_aggregate_and_calculate(self):
        ds = _make_dataset(columns=["store", "upc", "quantity"], has_quantity=True)
        assert suggest_mode(ds) == ProcessingMode.AGGREGATE_AND_CALCULATE

    def test_suggests_aggregate_only(self):
        ds = _make_dataset(columns=["store", "upc"], has_quantity=False)
        assert suggest_mode(ds) == ProcessingMode.AGGREGATE_ONLY

    def test_suggests_raw_review(self):
        ds = _make_dataset(columns=["upc", "description"], has_quantity=False)
        assert suggest_mode(ds) == ProcessingMode.RAW_REVIEW


class TestSelectMode:
    def test_select_available_mode(self):
        ds = _make_dataset(columns=["store", "upc", "quantity"], has_quantity=True)
        result = select_mode(ProcessingMode.AGGREGATE_AND_CALCULATE, ds)
        assert result == ProcessingMode.AGGREGATE_AND_CALCULATE

    def test_select_unavailable_falls_back(self):
        ds = _make_dataset(columns=["upc", "description"], has_quantity=False)
        result = select_mode(ProcessingMode.AGGREGATE_ONLY, ds)
        assert result == ProcessingMode.RAW_REVIEW

    def test_select_raw_review_always_works(self):
        ds = _make_dataset(columns=["upc"], has_quantity=False)
        result = select_mode(ProcessingMode.RAW_REVIEW, ds)
        assert result == ProcessingMode.RAW_REVIEW

    def test_select_with_none_dataset(self):
        result = select_mode(ProcessingMode.AGGREGATE_ONLY, None)
        assert result == ProcessingMode.RAW_REVIEW

    def test_select_raw_review_with_none_dataset(self):
        result = select_mode(ProcessingMode.RAW_REVIEW, None)
        assert result == ProcessingMode.RAW_REVIEW
