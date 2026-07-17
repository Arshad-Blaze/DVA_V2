"""Unit tests for preview generation."""

import pytest

from dav_platform.detection.previews import (
    generate_raw_preview,
    generate_flatten_preview,
    generate_canonical_preview,
)
from dav_platform.core.contracts import FileType, RecordTypeInfo


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
    def test_with_mapping(self):
        import polars as pl
        df = pl.DataFrame({"field_0": ["Apple"], "field_1": ["1.50"]})
        candidates = {"price": [type('obj', (object,), {'physical_column': 'field_1'})()]}
        result = generate_canonical_preview(df, candidates)
        assert result is not None

    def test_none_preview(self):
        result = generate_canonical_preview(None, {})
        assert result is None
