"""Tests for streaming canonical dataset."""

import pytest
import polars as pl

from dav_platform.canonical.streaming import estimate_memory_usage, transform_chunks
from dav_platform.core.contracts import DiscoveryResult, FileType


class TestEstimateMemoryUsage:
    def test_basic_estimate(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )
        estimate = estimate_memory_usage(result, total_rows=1000, avg_row_bytes=200)
        assert estimate["estimated_bytes"] == 200000
        assert estimate["chunk_recommendation"] == 5000

    def test_small_rows(self):
        result = DiscoveryResult(file_path="/test.csv", file_type=FileType.DELIMITED)
        estimate = estimate_memory_usage(result, total_rows=100, avg_row_bytes=50)
        assert estimate["chunk_recommendation"] == 10000

    def test_defaults(self):
        result = DiscoveryResult(file_path="/test.csv", file_type=FileType.DELIMITED)
        estimate = estimate_memory_usage(result)
        assert "chunk_recommendation" in estimate


class TestTransformChunks:
    def test_transforms_chunks(self):
        def chunk_generator():
            yield pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
            yield pl.DataFrame({"A": [3, 4], "B": ["z", "w"]})

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        datasets = list(transform_chunks(chunk_generator(), result))
        assert len(datasets) == 2
        assert datasets[0].dataframe is not None
