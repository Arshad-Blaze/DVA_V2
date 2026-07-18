"""Unit tests for preview generation."""

import pytest
import polars as pl

from dav_platform.canonical.preview import generate_canonical_preview
from dav_platform.detection.previews import (
    generate_raw_preview,
    generate_flatten_preview,
)
from dav_platform.core.contracts import ColumnMapping, FileType, RecordTypeInfo


class TestGenerateRawPreview:
    def test_basic_preview(self):
        lines = ["name,price", "Apple,1.50"]
        df = generate_raw_preview(lines)
        assert df is not None
        assert df.height == 2
        assert "line_number" in df.columns
        assert "content" in df.columns

    def test_max_rows(self):
        lines = [f"line{i}" for i in range(50)]
        df = generate_raw_preview(lines, max_rows=10)
        assert df.height == 10

    def test_empty_lines(self):
        df = generate_raw_preview([])
        assert df is None


class TestGenerateFlattenPreview:
    def test_delimited_preview(self):
        lines = ["name,price", "Apple,1.50"]
        df = generate_flatten_preview(lines, ",", FileType.DELIMITED, [], [])
        assert df is not None
        assert df.height == 2

    def test_with_record_types(self):
        lines = ["H|data", "D|data", "T|data"]
        rts = [RecordTypeInfo(prefix="H", frequency=1), RecordTypeInfo(prefix="D", frequency=1)]
        df = generate_flatten_preview(lines, "|", FileType.DELIMITED, rts, [])
        assert df is not None
        assert "record_type" in df.columns

    def test_empty_lines(self):
        df = generate_flatten_preview([], None, FileType.DELIMITED, [], [])
        assert df is None


class TestGenerateCanonicalPreview:
    def test_returns_none_for_none_input(self):
        result = generate_canonical_preview(None, [])
        assert result is None

    def test_returns_none_for_empty_mappings(self):
        df = pl.DataFrame({"field_0": [1], "field_2": ["x"]})
        result = generate_canonical_preview(df, [])
        assert result is None

    def test_renames_to_canonical_names(self):
        df = pl.DataFrame({"field_0": [1, 2], "field_1": ["x", "y"]})
        mappings = [
            ColumnMapping(physical_column="S", canonical_name="store"),
            ColumnMapping(physical_column="U", canonical_name="upc"),
        ]
        result = generate_canonical_preview(df, mappings)
        assert "store" in result.columns
        assert "upc" in result.columns
        assert "field_0" not in result.columns

    def test_max_rows_applied(self):
        df = pl.DataFrame({"field_0": list(range(50))})
        mappings = [ColumnMapping(physical_column="S", canonical_name="store")]
        result = generate_canonical_preview(df, mappings, max_rows=5)
        assert result.height == 5

    def test_no_retailer_columns_exposed(self):
        df = pl.DataFrame({"field_0": [1], "field_1": ["A"], "physical_col": [99]})
        mappings = [
            ColumnMapping(physical_column="physical_col", canonical_name="store"),
        ]
        result = generate_canonical_preview(df, mappings)
        assert "physical_col" not in result.columns
        assert result.columns == ["store"]

    def test_no_record_type_exposed(self):
        df = pl.DataFrame({"field_0": [1], "_record_type": ["D"]})
        mappings = [ColumnMapping(physical_column="S", canonical_name="store")]
        result = generate_canonical_preview(df, mappings)
        assert "_record_type" not in result.columns
        assert result.columns == ["store"]

    def test_only_mapped_canonical_columns_returned(self):
        df = pl.DataFrame({"field_0": [1, 2], "field_1": ["x", "y"], "field_2": [10, 20]})
        mappings = [
            ColumnMapping(physical_column="S", canonical_name="store"),
            ColumnMapping(physical_column="U", canonical_name="upc"),
        ]
        result = generate_canonical_preview(df, mappings)
        assert result.columns == ["store", "upc"]
        assert "field_2" not in result.columns



