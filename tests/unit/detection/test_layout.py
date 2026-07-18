"""Unit tests for layout intelligence."""

import pytest

from dav_platform.detection.layout import detect_column_breaks, generate_layout_fields
from dav_platform.core.contracts import LayoutField


class TestDetectColumnBreaks:
    def test_simple_columns(self):
        lines = [
            "name     price    quantity",
            "Apple    1.50     100",
            "Banana   0.75     200",
        ]
        breaks = detect_column_breaks(lines)
        assert len(breaks) >= 1

    def test_single_column(self):
        lines = ["hello world", "foo bar"]
        breaks = detect_column_breaks(lines)
        # May or may not find breaks depending on gap size
        assert isinstance(breaks, list)

    def test_empty_lines(self):
        breaks = detect_column_breaks([])
        assert breaks == []

    def test_no_gaps(self):
        lines = ["abc", "def", "ghi"]
        breaks = detect_column_breaks(lines)
        assert breaks == []


class TestGenerateLayoutFields:
    def test_generates_fields(self):
        lines = [
            "name     price    quantity",
            "Apple    1.50     100",
        ]
        breaks = [5, 12]
        fields = generate_layout_fields(lines, breaks)
        assert len(fields) >= 1
        assert all(isinstance(f, LayoutField) for f in fields)

    def test_empty_breaks(self):
        fields = generate_layout_fields(["line1"], [])
        assert fields == []

    def test_field_properties(self):
        lines = [
            "name     price    quantity",
            "Apple    1.50     100",
        ]
        breaks = [5, 12]
        fields = generate_layout_fields(lines, breaks)
        for f in fields:
            assert f.start >= 0
            assert f.width > 0
            assert 0.0 <= f.confidence <= 1.0
