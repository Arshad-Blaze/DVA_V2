"""Unit tests for delimiter detection."""

import pytest

from dav_platform.detection.delimiter import (
    count_delimiters_outside_quotes,
    detect_delimiter,
    validate_delimiter_consistency,
)


class TestCountDelimitersOutsideQuotes:
    def test_simple_csv(self):
        assert count_delimiters_outside_quotes("a,b,c", ",") == 2

    def test_quoted_delimiter(self):
        assert count_delimiters_outside_quotes('a,"b,c",d', ",") == 2

    def test_pipe_delimiter(self):
        assert count_delimiters_outside_quotes("a|b|c", "|") == 2

    def test_tab_delimiter(self):
        assert count_delimiters_outside_quotes("a\tb\tc", "\t") == 2

    def test_no_delimiter(self):
        assert count_delimiters_outside_quotes("abc", ",") == 0


class TestDetectDelimiter:
    def test_csv(self):
        lines = ["name,price,quantity", "Apple,1.50,100", "Banana,0.75,200"]
        delim, scores = detect_delimiter(lines)
        assert delim == ","
        assert scores[","] == 6

    def test_pipe(self):
        lines = ["name|price|quantity", "Apple|1.50|100"]
        delim, scores = detect_delimiter(lines)
        assert delim == "|"

    def test_empty_lines(self):
        delim, scores = detect_delimiter([])
        assert delim is None
        assert scores == {}

    def test_fixed_width(self):
        lines = ["name     price    quantity", "Apple    1.50     100"]
        delim, scores = detect_delimiter(lines)
        assert delim is None


class TestValidateDelimiterConsistency:
    def test_perfect_consistency(self):
        lines = ["a,b,c", "d,e,f", "g,h,i"]
        assert validate_delimiter_consistency(lines, ",") == 1.0

    def test_no_delimiter(self):
        lines = ["abc", "def"]
        assert validate_delimiter_consistency(lines, ",") == 0.0

    def test_empty_lines(self):
        assert validate_delimiter_consistency([], ",") == 0.0
