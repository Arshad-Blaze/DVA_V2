"""Unit tests for multiline detection."""

import pytest

from dav_platform.detection.multiline import (
    detect_multiline,
    detect_record_types,
    detect_trailer_prefix,
)


class TestDetectMultiline:
    def test_delimited_multiline(self):
        lines = [
            "H|STORE001|2024-01-01",
            "D|ITEM001|100",
            "D|ITEM002|200",
            "T|2",
        ]
        assert detect_multiline(lines) is True

    def test_fixed_width_multiline(self):
        lines = [
            "HDR001STORE001",
            "DTL002ITEM001100",
            "DTL003ITEM002200",
            "TRL004COUNT002",
        ]
        assert detect_multiline(lines) is True

    def test_backslash_continuation(self):
        lines = [
            "line1\\",
            "line2\\",
            "line3\\",
            "line4\\",
            "line5\\",
            "line6",
        ]
        assert detect_multiline(lines) is True

    def test_simple_csv(self):
        lines = [
            "name,price,quantity",
            "Apple,1.50,100",
            "Banana,0.75,200",
        ]
        assert detect_multiline(lines) is False

    def test_empty_lines(self):
        assert detect_multiline([]) is False


class TestDetectRecordTypes:
    def test_delimited_records(self):
        lines = ["H|data", "D|data", "T|data"]
        assert detect_record_types(lines, "|") == ["D", "H", "T"]

    def test_no_records(self):
        lines = ["12345", "67890"]
        assert detect_record_types(lines) == []

    def test_empty_lines(self):
        assert detect_record_types([]) == []


class TestDetectTrailerPrefix:
    def test_trl_prefix(self):
        lines = [
            "H|data",
            "D|data",
            "D|data",
            "TRL|2",
            "TRL|count",
        ]
        assert detect_trailer_prefix(lines) == "TRL"

    def test_t_prefix(self):
        lines = [
            "H|data",
            "D|data",
            "D|data",
            "T|2",
            "T|count",
        ]
        assert detect_trailer_prefix(lines) == "T"

    def test_no_trailer(self):
        lines = ["H|data", "D|data"]
        assert detect_trailer_prefix(lines) is None

    def test_empty_lines(self):
        assert detect_trailer_prefix([]) is None
