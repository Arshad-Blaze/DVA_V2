"""Tests for multiline flattening."""

import pytest

from dav_platform.canonical.multiline import flatten_multiline
from dav_platform.core.contracts import RecordTypeInfo


class TestFlattenMultiline:
    def test_single_line_records(self):
        lines = ["D|123|Apple", "D|456|Banana"]
        rts = [RecordTypeInfo(prefix="D", frequency=2)]
        rows = flatten_multiline(lines, delimiter="|", record_types=rts)
        assert len(rows) == 2

    def test_continuation_lines(self):
        lines = [
            "U|12345|Product A",
            "  Continuation data 1",
            "  Continuation data 2",
            "U|67890|Product B",
        ]
        rts = [RecordTypeInfo(prefix="U", frequency=2)]
        rows = flatten_multiline(lines, delimiter="|", record_types=rts)
        assert len(rows) == 2
        # First row should have continuation data
        assert "field_3" in rows[0] or len(rows[0]) > 4

    def test_empty_lines(self):
        rows = flatten_multiline([], delimiter="|")
        assert len(rows) == 0

    def test_blank_lines_skipped(self):
        lines = ["D|1|A", "", "  ", "D|2|B"]
        rts = [RecordTypeInfo(prefix="D", frequency=2)]
        rows = flatten_multiline(lines, delimiter="|", record_types=rts)
        assert len(rows) == 2

    def test_no_delimiter(self):
        lines = ["D12345", "D67890"]
        rts = [RecordTypeInfo(prefix="D", frequency=2)]
        rows = flatten_multiline(lines, record_types=rts)
        assert len(rows) == 2
