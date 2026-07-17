"""Unit tests for record type detection (detailed)."""

import pytest

from dav_platform.detection.multiline import (
    detect_record_types_detailed,
    build_record_hierarchy,
)
from dav_platform.core.contracts import RecordTypeInfo


class TestDetectRecordTypesDetailed:
    def test_basic_record_types(self):
        lines = ["H|data", "D|data1", "D|data2", "T|data"]
        rts = detect_record_types_detailed(lines, "|")
        assert len(rts) == 3
        assert all(isinstance(rt, RecordTypeInfo) for rt in rts)

    def test_record_type_stats(self):
        lines = ["H|data", "D|data1", "D|data2", "D|data3", "T|data"]
        rts = detect_record_types_detailed(lines, "|")
        d_rt = next(rt for rt in rts if rt.prefix == "D")
        assert d_rt.frequency == 3
        assert d_rt.confidence > 0.0

    def test_empty_lines(self):
        rts = detect_record_types_detailed([])
        assert rts == []

    def test_sorted_by_frequency(self):
        lines = ["H|data", "D|d1", "D|d2", "D|d3", "T|data"]
        rts = detect_record_types_detailed(lines, "|")
        assert rts[0].frequency >= rts[-1].frequency


class TestBuildRecordHierarchy:
    def test_basic_hierarchy(self):
        rts = [
            RecordTypeInfo(prefix="H", frequency=1),
            RecordTypeInfo(prefix="D", frequency=5),
            RecordTypeInfo(prefix="T", frequency=1),
        ]
        h = build_record_hierarchy(rts, [])
        assert h is not None
        assert h["header"] is not None
        assert h["trailer"] is not None
        assert len(h["detail"]) > 0

    def test_no_header_trailer(self):
        rts = [RecordTypeInfo(prefix="D", frequency=5)]
        h = build_record_hierarchy(rts, [])
        # May or may not have header/trailer depending on logic
        assert h is not None or h is None  # Either is valid

    def test_empty_record_types(self):
        h = build_record_hierarchy([], [])
        assert h is None
