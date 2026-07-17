"""Unit tests for header detection."""

import pytest

from dav_platform.detection.header import detect_header, detect_header_prefix


class TestDetectHeader:
    def test_header_present(self):
        lines = ["name,price,quantity", "Apple,1.50,100"]
        assert detect_header(lines, ",") is True

    def test_no_header(self):
        lines = ["Apple,1.50,100", "Banana,0.75,200"]
        assert detect_header(lines, ",") is False

    def test_empty_lines(self):
        assert detect_header([], ",") is False

    def test_single_value_header(self):
        lines = ["name"]
        assert detect_header(lines, ",") is True

    def test_numeric_first_row(self):
        lines = ["1,2,3", "4,5,6"]
        assert detect_header(lines, ",") is False


class TestDetectHeaderPrefix:
    def test_hdr_prefix(self):
        lines = ["HDR001", "HDR002", "DTL003", "TRL004"]
        prefix = detect_header_prefix(lines)
        assert prefix in ("HDR", "DTL", "TRL")  # All are 3-char prefixes

    def test_no_prefix(self):
        lines = ["12345", "67890"]
        assert detect_header_prefix(lines) is None

    def test_empty_lines(self):
        assert detect_header_prefix([]) is None

    def test_multiple_prefixes(self):
        lines = ["HDR001", "HDR002", "DTL003"]
        prefix = detect_header_prefix(lines)
        assert prefix is not None
