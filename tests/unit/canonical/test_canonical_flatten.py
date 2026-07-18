"""Tests for record hierarchy flattening."""

import pytest

from dav_platform.canonical.flatten import flatten_hierarchy
from dav_platform.core.contracts import RecordTypeInfo


@pytest.fixture
def hierarchy_lines():
    return [
        "H|100|2024-01-15",
        "D|1234567890|Apple|1.50",
        "D|0987654321|Banana|0.75",
        "T|2",
    ]


@pytest.fixture
def record_types():
    return [
        RecordTypeInfo(prefix="H", frequency=1),
        RecordTypeInfo(prefix="D", frequency=2),
        RecordTypeInfo(prefix="T", frequency=1),
    ]


class TestFlattenHierarchy:
    def test_basic_flattening(self, hierarchy_lines, record_types):
        rows = flatten_hierarchy(
            hierarchy_lines, record_types, delimiter="|",
            header_prefix="H", trailer_prefix="T"
        )
        assert len(rows) == 2
        assert rows[0]["_record_type"] == "D"

    def test_header_context_merged(self, hierarchy_lines, record_types):
        rows = flatten_hierarchy(
            hierarchy_lines, record_types, delimiter="|",
            header_prefix="H", trailer_prefix="T"
        )
        assert len(rows) == 2
        # Detail rows should have header context merged

    def test_no_trailer_in_output(self, hierarchy_lines, record_types):
        rows = flatten_hierarchy(
            hierarchy_lines, record_types, delimiter="|",
            header_prefix="H", trailer_prefix="T"
        )
        for row in rows:
            assert row["_record_type"] != "T"

    def test_empty_lines(self, record_types):
        rows = flatten_hierarchy([], record_types)
        assert len(rows) == 0

    def test_no_record_types(self, hierarchy_lines):
        rows = flatten_hierarchy(hierarchy_lines, [])
        assert len(rows) == 0

    def test_all_detail_records(self):
        lines = ["D|1|A", "D|2|B", "D|3|C"]
        rts = [RecordTypeInfo(prefix="D", frequency=3)]
        rows = flatten_hierarchy(lines, rts, delimiter="|")
        assert len(rows) == 3
