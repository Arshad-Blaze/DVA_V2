"""Tests for fixed-width transformation."""

import pytest

from dav_platform.canonical.fixed_width import (
    apply_datatype_conversions,
    fixed_width_to_dataframe,
    transform_fixed_width,
)
from dav_platform.core.contracts import LayoutField


@pytest.fixture
def layout_fields():
    return [
        LayoutField(start=0, width=5, probable_name="store"),
        LayoutField(start=5, width=10, probable_name="upc"),
        LayoutField(start=15, width=8, probable_name="price"),
    ]


@pytest.fixture
def sample_lines():
    return [
        "  1  1234567890    1.50",
        "  2  0987654321    2.75",
        "  3  1111111111    0.99",
    ]


class TestTransformFixedWidth:
    def test_basic_transform(self, sample_lines, layout_fields):
        rows = transform_fixed_width(sample_lines, layout_fields)
        assert len(rows) == 3
        assert rows[0]["store"] == "1"
        assert rows[0]["upc"] == "1234567890"
        assert rows[0]["price"] == "1.50"

    def test_skip_header(self, sample_lines, layout_fields):
        lines = ["HEADER"] + sample_lines
        rows = transform_fixed_width(lines, layout_fields, header_prefix="HEADER")
        assert len(rows) == 3

    def test_skip_trailer(self, sample_lines, layout_fields):
        lines = sample_lines + ["TRAILER"]
        rows = transform_fixed_width(lines, layout_fields, trailer_prefix="TRAILER")
        assert len(rows) == 3

    def test_empty_lines(self, layout_fields):
        rows = transform_fixed_width([], layout_fields)
        assert len(rows) == 0

    def test_line_number_tracking(self, sample_lines, layout_fields):
        rows = transform_fixed_width(sample_lines, layout_fields)
        assert rows[0]["_line_number"] == 1
        assert rows[2]["_line_number"] == 3


class TestFixedWidthToDataframe:
    def test_creates_dataframe(self, sample_lines, layout_fields):
        df = fixed_width_to_dataframe(sample_lines, layout_fields)
        assert df is not None
        assert df.height == 3

    def test_empty_returns_none(self, layout_fields):
        df = fixed_width_to_dataframe([], layout_fields)
        assert df is None


class TestApplyDatatypeConversions:
    def test_numeric_conversion(self):
        import polars as pl
        df = pl.DataFrame({"price": ["1.50", "2.75", "0.99"]})
        fields = [LayoutField(start=0, width=8, probable_name="price", datatype="numeric")]
        result = apply_datatype_conversions(df, fields)
        assert result["price"].dtype == pl.Float64

    def test_integer_conversion(self):
        import polars as pl
        df = pl.DataFrame({"store": ["1", "2", "3"]})
        fields = [LayoutField(start=0, width=5, probable_name="store", datatype="integer")]
        result = apply_datatype_conversions(df, fields)
        assert result["store"].dtype == pl.Int64

    def test_none_dataframe(self):
        result = apply_datatype_conversions(None, [])
        assert result is None
