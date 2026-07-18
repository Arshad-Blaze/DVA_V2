"""Unit tests for type coercion."""

import pytest

from dav_platform.canonical.coercion import (
    coerce_date,
    coerce_integer,
    coerce_numeric,
)


class TestCoerceNumeric:
    def test_integer(self):
        assert coerce_numeric(42) == 42.0

    def test_float(self):
        assert coerce_numeric(3.14) == 3.14

    def test_string_number(self):
        assert coerce_numeric("123.45") == 123.45

    def test_empty_string(self):
        assert coerce_numeric("") is None

    def test_none(self):
        assert coerce_numeric(None) is None

    def test_non_numeric(self):
        assert coerce_numeric("abc") is None


class TestCoerceInteger:
    def test_integer(self):
        assert coerce_integer(42) == 42

    def test_float_to_int(self):
        assert coerce_integer(3.0) == 3

    def test_string_number(self):
        assert coerce_integer("123") == 123

    def test_string_float(self):
        assert coerce_integer("123.45") == 123

    def test_empty_string(self):
        assert coerce_integer("") is None

    def test_none(self):
        assert coerce_integer(None) is None


class TestCoerceDate:
    def test_iso_format(self):
        assert coerce_date("2024-01-15") == "2024-01-15"

    def test_us_format(self):
        assert coerce_date("01/15/2024") == "2024-01-15"

    def test_compact_format(self):
        assert coerce_date("20240115") == "2024-01-15"

    def test_none(self):
        assert coerce_date(None) is None

    def test_empty_string(self):
        assert coerce_date("") is None

    def test_invalid_date(self):
        assert coerce_date("not-a-date") is None
