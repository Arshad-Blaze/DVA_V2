"""Tests for capability detection."""

import pytest

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
)
from dav_platform.requirements.capability import detect_capabilities, get_capability_summary


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


class TestDetectCapabilities:
    def test_none_dataset(self):
        cap = detect_capabilities(None)
        assert cap.can_review is True
        assert cap.can_aggregate is False
        assert cap.can_calculate is False

    def test_full_capabilities(self):
        cap = detect_capabilities(_make_dataset())
        assert cap.can_review is True
        assert cap.can_aggregate is True
        assert cap.can_calculate is True
        assert cap.can_validate is True
        assert cap.can_migrate is True
        assert cap.can_report is True
        assert cap.can_compare is False  # needs second dataset

    def test_no_groupable(self):
        cap = detect_capabilities(_make_dataset(columns=["upc", "description"]))
        assert cap.can_aggregate is False
        assert cap.can_calculate is False
        assert cap.can_report is False

    def test_groupable_no_quantity(self):
        cap = detect_capabilities(_make_dataset(columns=["store", "upc"], has_quantity=False))
        assert cap.can_aggregate is True
        assert cap.can_calculate is False
        assert cap.can_report is True

    def test_no_data(self):
        ds = _make_dataset(has_data=False)
        cap = detect_capabilities(ds)
        assert cap.can_review is False
        assert cap.can_aggregate is False


class TestGetCapabilitySummary:
    def test_full_capabilities(self):
        cap = detect_capabilities(_make_dataset())
        summary = get_capability_summary(cap)
        assert "aggregate" in summary
        assert "calculate" in summary
        assert "review" in summary

    def test_no_capabilities(self):
        from dav_platform.core.contracts import CapabilityMatrix
        cap = CapabilityMatrix()
        summary = get_capability_summary(cap)
        assert "No capabilities" in summary
