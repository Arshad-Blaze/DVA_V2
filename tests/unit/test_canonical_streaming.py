"""Tests for streaming canonical dataset."""

import pytest
import polars as pl

from dav_platform.canonical.streaming import estimate_memory_usage, transform_chunks
from dav_platform.core.contracts import DiscoveryResult, FileType


class TestEstimateMemoryUsage:
    def test_basic_estimate(self):
        estimate = estimate_memory_usage(total_rows=1000, avg_row_bytes=200)
        assert estimate["estimated_bytes"] == 200000
        assert estimate["chunk_recommendation"] == 5000

    def test_small_rows(self):
        estimate = estimate_memory_usage(total_rows=100, avg_row_bytes=50)
        assert estimate["chunk_recommendation"] == 10000

    def test_defaults(self):
        estimate = estimate_memory_usage()
        assert "chunk_recommendation" in estimate
        assert estimate["estimated_rows"] == 10000

    def test_zero_rows_defaults(self):
        estimate = estimate_memory_usage(total_rows=0)
        assert estimate["estimated_rows"] == 10000

    def test_negative_rows_defaults(self):
        estimate = estimate_memory_usage(total_rows=-5)
        assert estimate["estimated_rows"] == 10000

    def test_large_row_bytes(self):
        estimate = estimate_memory_usage(total_rows=100, avg_row_bytes=1000)
        assert estimate["chunk_recommendation"] == 1000
        assert estimate["estimated_bytes"] == 100000

    def test_medium_row_bytes(self):
        estimate = estimate_memory_usage(total_rows=100, avg_row_bytes=300)
        assert estimate["chunk_recommendation"] == 5000


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

    def test_empty_chunks_skipped(self):
        def chunk_generator():
            yield pl.DataFrame({"A": [1]})
            yield pl.DataFrame({"A": []})  # empty
            yield pl.DataFrame({"A": [2]})

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        datasets = list(transform_chunks(chunk_generator(), result))
        assert len(datasets) == 2

    def test_none_chunks_skipped(self):
        def chunk_generator():
            yield pl.DataFrame({"A": [1]})
            yield None
            yield pl.DataFrame({"A": [2]})

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        datasets = list(transform_chunks(chunk_generator(), result))
        assert len(datasets) == 2

    def test_all_empty_chunks(self):
        def chunk_generator():
            yield pl.DataFrame({"A": []})
            yield None

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        datasets = list(transform_chunks(chunk_generator(), result))
        assert len(datasets) == 0

    def test_single_chunk(self):
        def chunk_generator():
            yield pl.DataFrame({"A": [1, 2, 3]})

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        datasets = list(transform_chunks(chunk_generator(), result))
        assert len(datasets) == 1
