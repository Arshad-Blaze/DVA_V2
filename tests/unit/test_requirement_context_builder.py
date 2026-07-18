"""Tests for context builder."""

import pytest

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ProcessingMode,
)
from dav_platform.requirements.context_builder import (
    build_context,
    build_session_id,
    extract_metadata,
)


def _make_dataset(columns=None, has_quantity=True, has_data=True):
    """Helper to create test CanonicalDataset."""
    if columns is None:
        columns = ["store", "upc", "quantity"]

    metadata = CanonicalMetadata(
        total_rows=10 if has_data else 0,
        mapped_columns=len(columns),
        quantity_column="quantity" if has_quantity else None,
        quantity_type="unit" if has_quantity else "none",
        confidence=0.95,
        source_file_type="delimited",
        encoding="utf-8",
        flatten_strategy="direct",
        uom_strategy="detected",
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
        warnings=["test warning"],
        recommendations=["test recommendation"],
    )


class TestBuildSessionId:
    def test_generates_uuid(self):
        sid = build_session_id()
        assert isinstance(sid, str)
        assert len(sid) == 36  # UUID format
        assert "-" in sid

    def test_unique_ids(self):
        ids = {build_session_id() for _ in range(100)}
        assert len(ids) == 100


class TestExtractMetadata:
    def test_none_dataset(self):
        meta = extract_metadata(None)
        assert meta == {"has_data": False}

    def test_full_metadata(self):
        ds = _make_dataset()
        meta = extract_metadata(ds)

        assert meta["file_path"] == "/test.csv"
        assert meta["total_rows"] == 10
        assert meta["canonical_columns"] == ["store", "upc", "quantity"]
        assert meta["quantity_column"] == "quantity"
        assert meta["quantity_type"] == "unit"
        assert meta["confidence"] == 0.95
        assert meta["source_file_type"] == "delimited"
        assert meta["encoding"] == "utf-8"
        assert meta["flatten_strategy"] == "direct"
        assert meta["uom_strategy"] == "detected"
        assert meta["has_data"] is True
        assert meta["row_count"] == 1
        assert "test warning" in meta["warnings"]
        assert "test recommendation" in meta["recommendations"]

    def test_no_data(self):
        ds = _make_dataset(has_data=False)
        meta = extract_metadata(ds)
        assert meta["has_data"] is False
        assert meta["row_count"] == 0

    def test_no_quantity(self):
        ds = _make_dataset(has_quantity=False)
        meta = extract_metadata(ds)
        assert meta["quantity_column"] is None
        assert meta["quantity_type"] == "none"


class TestBuildContext:
    def test_basic_context(self):
        ds = _make_dataset()
        ctx = build_context(ProcessingMode.AGGREGATE_AND_CALCULATE, ds)

        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert ctx.options == {}
        assert isinstance(ctx.session_id, str)
        assert ctx.metadata["file_path"] == "/test.csv"

    def test_with_options(self):
        ds = _make_dataset()
        opts = {"group_by": "store", "calculate": "sum"}
        ctx = build_context(ProcessingMode.AGGREGATE_ONLY, ds, options=opts)

        assert ctx.options == opts

    def test_with_session_id(self):
        ds = _make_dataset()
        ctx = build_context(ProcessingMode.RAW_REVIEW, ds, session_id="test-123")
        assert ctx.session_id == "test-123"

    def test_auto_generates_session_id(self):
        ds = _make_dataset()
        ctx = build_context(ProcessingMode.RAW_REVIEW, ds)
        assert isinstance(ctx.session_id, str)
        assert len(ctx.session_id) == 36

    def test_none_dataset(self):
        ctx = build_context(ProcessingMode.RAW_REVIEW, None)
        assert ctx.mode == ProcessingMode.RAW_REVIEW
        assert ctx.metadata["has_data"] is False
