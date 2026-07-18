"""Tests for Requirement Layer engine."""

import pytest

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    OperationContext,
    ProcessingMode,
)
from dav_platform.requirements.engine import RequirementLayer


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
        confidence=0.95,
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


class TestRequirementLayerProcess:
    def test_auto_suggests_mode(self):
        layer = RequirementLayer()
        ds = _make_dataset(columns=["store", "upc", "quantity"], has_quantity=True)
        ctx = layer.process(dataset=ds)

        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert isinstance(ctx, OperationContext)

    def test_explicit_mode(self):
        layer = RequirementLayer()
        ds = _make_dataset(columns=["store", "upc"])
        ctx = layer.process(dataset=ds, mode=ProcessingMode.AGGREGATE_ONLY)

        assert ctx.mode == ProcessingMode.AGGREGATE_ONLY

    def test_unavailable_mode_falls_back(self):
        layer = RequirementLayer()
        ds = _make_dataset(columns=["upc", "description"], has_quantity=False)
        ctx = layer.process(dataset=ds, mode=ProcessingMode.AGGREGATE_ONLY)

        assert ctx.mode == ProcessingMode.RAW_REVIEW

    def test_none_dataset(self):
        layer = RequirementLayer()
        ctx = layer.process(dataset=None)

        assert ctx.mode == ProcessingMode.RAW_REVIEW
        assert ctx.metadata["has_data"] is False

    def test_with_options(self):
        layer = RequirementLayer()
        ds = _make_dataset()
        opts = {"group_by": "store"}
        ctx = layer.process(dataset=ds, options=opts)

        assert ctx.options == opts

    def test_session_id_generated(self):
        layer = RequirementLayer()
        ds = _make_dataset()
        ctx = layer.process(dataset=ds)

        assert isinstance(ctx.session_id, str)
        assert len(ctx.session_id) == 36

    def test_validation_in_metadata(self):
        layer = RequirementLayer()
        ds = _make_dataset()
        ctx = layer.process(dataset=ds)

        assert "validation" in ctx.metadata
        assert ctx.metadata["validation"]["passed"] is True

    def test_validation_failure_direct(self):
        """Test validation failure via direct validator call."""
        from dav_platform.requirements.validator import validate_mode
        ds = _make_dataset(columns=["upc", "description"], has_quantity=False)
        result = validate_mode(ProcessingMode.AGGREGATE_AND_CALCULATE, ds)
        assert result.passed is False
        assert len(result.issues) > 0

    def test_validation_records_result(self):
        """Test that engine records validation result in metadata."""
        layer = RequirementLayer()
        ds = _make_dataset()
        ctx = layer.process(dataset=ds)
        assert "validation" in ctx.metadata
        assert ctx.metadata["validation"]["passed"] is True

    def test_metadata_populated(self):
        layer = RequirementLayer()
        ds = _make_dataset()
        ctx = layer.process(dataset=ds)

        assert ctx.metadata["file_path"] == "/test.csv"
        assert ctx.metadata["total_rows"] == 10
        assert "store" in ctx.metadata["canonical_columns"]


class TestRequirementLayerGetAvailableModes:
    def test_with_dataset(self):
        layer = RequirementLayer()
        ds = _make_dataset(columns=["store", "upc", "quantity"], has_quantity=True)
        modes = layer.get_available_modes(ds)

        assert ProcessingMode.RAW_REVIEW in modes
        assert ProcessingMode.AGGREGATE_ONLY in modes
        assert ProcessingMode.AGGREGATE_AND_CALCULATE in modes

    def test_with_none(self):
        layer = RequirementLayer()
        modes = layer.get_available_modes(None)
        assert modes == [ProcessingMode.RAW_REVIEW]


class TestRequirementLayerCheckReadiness:
    def test_ready_dataset(self):
        layer = RequirementLayer()
        ds = _make_dataset()
        issues = layer.check_readiness(ds)
        assert issues == []

    def test_none_dataset(self):
        layer = RequirementLayer()
        issues = layer.check_readiness(None)
        assert "No dataset provided" in issues
