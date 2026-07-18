"""Unit tests for statistics collection."""

import pytest

from dav_platform.detection.statistics import collect_statistics
from dav_platform.core.contracts import DetectionStatistics


class TestCollectStatistics:
    def test_basic_stats(self):
        lines = ["name,price", "Apple,1.50", "Banana,0.75"]
        stats = collect_statistics(lines, delimiter=",")
        assert isinstance(stats, DetectionStatistics)
        assert stats.record_count == 3
        assert stats.avg_record_length > 0
        assert stats.min_record_length > 0
        assert stats.max_record_length > 0

    def test_delimiter_stats(self):
        lines = ["a,b,c", "d,e,f", "g,h,i"]
        stats = collect_statistics(lines, delimiter=",")
        assert "avg_field_count" in stats.delimiter_statistics
        assert stats.delimiter_statistics["avg_field_count"] == 3

    def test_empty_lines(self):
        stats = collect_statistics([])
        assert stats.record_count == 0

    def test_character_distribution(self):
        lines = ["abc", "def"]
        stats = collect_statistics(lines)
        assert len(stats.character_distribution) > 0

    def test_record_statistics(self):
        lines = ["short", "a longer line"]
        stats = collect_statistics(lines)
        assert "length_distribution" in stats.record_statistics
