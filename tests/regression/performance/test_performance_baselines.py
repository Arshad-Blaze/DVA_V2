"""Performance baseline tests for the canonical pipeline.

Establishes timing baselines for streaming transforms, chunk processing,
memory estimation, and UOM normalization.
"""

import time

import pytest
import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.canonical.streaming import estimate_memory_usage, transform_chunks
from dav_platform.canonical.uom import normalize_uom
from dav_platform.core.contracts import (
    CandidateMapping,
    DiscoveryResult,
    FileType,
)


def _make_discovery_result(
    columns: list[str] | None = None,
    candidate_store: list[CandidateMapping] | None = None,
    candidate_upc: list[CandidateMapping] | None = None,
    candidate_units: list[CandidateMapping] | None = None,
    candidate_price: list[CandidateMapping] | None = None,
    candidate_uom: list[CandidateMapping] | None = None,
) -> DiscoveryResult:
    """Build a minimal DiscoveryResult for performance tests."""
    return DiscoveryResult(
        file_path="/perf_test.csv",
        file_type=FileType.DELIMITED,
        delimiter=",",
        columns=columns or [],
        has_header=True,
        confidence=0.9,
        candidate_store=candidate_store or [],
        candidate_upc=candidate_upc or [],
        candidate_units=candidate_units or [],
        candidate_price=candidate_price or [],
        candidate_uom=candidate_uom or [],
    )


def _make_large_df(n_rows: int) -> pl.DataFrame:
    """Create a large DataFrame with store, upc, units, price columns."""
    return pl.DataFrame({
        "Store": [f"S{i % 100:03d}" for i in range(n_rows)],
        "UPC": [f"{100000000000 + i}" for i in range(n_rows)],
        "Units": [i % 50 + 1 for i in range(n_rows)],
        "Price": [round((i % 100) * 1.5 + 0.99, 2) for i in range(n_rows)],
    })


@pytest.mark.performance
@pytest.mark.regression
class TestStreamingPerformance:
    """Verify streaming transform handles 100k rows in <2s."""

    @pytest.mark.slow
    def test_streaming_100k_rows_under_2s(self):
        n_rows = 100_000
        df = _make_large_df(n_rows)

        result = _make_discovery_result(
            columns=["Store", "UPC", "Units", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_units=[CandidateMapping(physical_column="Units", confidence=0.8)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.85)],
        )

        def chunk_gen():
            yield df

        start = time.perf_counter()
        datasets = list(transform_chunks(chunk_gen(), result))
        elapsed = time.perf_counter() - start

        assert len(datasets) == 1
        assert datasets[0].dataframe is not None
        assert datasets[0].dataframe.height == n_rows
        assert elapsed < 2.0, f"Streaming 100k rows took {elapsed:.2f}s (limit: 2.0s)"


@pytest.mark.performance
@pytest.mark.regression
class TestChunkProcessingPerformance:
    """Verify chunk processing works with various chunk sizes."""

    @pytest.mark.parametrize("chunk_size", [100, 1_000, 10_000])
    def test_chunk_sizes_process_all_rows(self, chunk_size: int):
        total_rows = 10_000
        result = _make_discovery_result(
            columns=["Store", "UPC", "Units", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_units=[CandidateMapping(physical_column="Units", confidence=0.8)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.85)],
        )

        def chunk_gen():
            offset = 0
            while offset < total_rows:
                batch = min(chunk_size, total_rows - offset)
                yield pl.DataFrame({
                    "Store": [f"S{i % 10:03d}" for i in range(offset, offset + batch)],
                    "UPC": [f"{100000 + i}" for i in range(offset, offset + batch)],
                    "Units": [1] * batch,
                    "Price": [9.99] * batch,
                })
                offset += batch

        datasets = list(transform_chunks(chunk_gen(), result, chunk_size=chunk_size))
        total_processed = sum(ds.dataframe.height for ds in datasets if ds.dataframe is not None)
        assert total_processed == total_rows


@pytest.mark.performance
@pytest.mark.regression
class TestMemoryEstimationAccuracy:
    """Verify estimate_memory_usage returns reasonable estimates."""

    def test_positive_rows_gives_positive_bytes(self):
        result = estimate_memory_usage(total_rows=1_000, avg_row_bytes=200)
        assert result["estimated_bytes"] > 0
        assert result["estimated_bytes"] == 200_000

    def test_recommended_chunk_size_is_positive_int(self):
        result = estimate_memory_usage(total_rows=5_000, avg_row_bytes=300)
        assert isinstance(result["chunk_recommendation"], int)
        assert result["chunk_recommendation"] > 0

    def test_zero_rows_uses_default(self):
        result = estimate_memory_usage(total_rows=0)
        assert result["estimated_rows"] == 10_000
        assert result["estimated_bytes"] > 0

    def test_large_rows_estimate(self):
        result = estimate_memory_usage(total_rows=100_000, avg_row_bytes=200)
        assert result["estimated_bytes"] == 20_000_000
        assert result["chunk_recommendation"] > 0

    def test_small_row_bytes_gets_larger_chunks(self):
        small = estimate_memory_usage(total_rows=1_000, avg_row_bytes=50)
        large = estimate_memory_usage(total_rows=1_000, avg_row_bytes=1_000)
        assert small["chunk_recommendation"] >= large["chunk_recommendation"]


@pytest.mark.performance
@pytest.mark.regression
class TestCanonicalTransformPerformance:
    """Verify CanonicalEngine.transform() handles 10k rows in <1s."""

    @pytest.mark.slow
    def test_transform_10k_rows_under_1s(self):
        n_rows = 10_000
        df = pl.DataFrame({
            "Store": [f"S{i % 50:03d}" for i in range(n_rows)],
            "UPC": [f"{100000 + i}" for i in range(n_rows)],
            "Units": [i % 20 + 1 for i in range(n_rows)],
            "Price": [round((i % 80) * 2.5 + 1.00, 2) for i in range(n_rows)],
        })

        result = _make_discovery_result(
            columns=["Store", "UPC", "Units", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_units=[CandidateMapping(physical_column="Units", confidence=0.8)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.85)],
        )

        engine = CanonicalEngine()

        start = time.perf_counter()
        dataset = engine.transform(result, data=df)
        elapsed = time.perf_counter() - start

        assert dataset.dataframe is not None
        assert dataset.dataframe.height == n_rows
        assert elapsed < 1.0, f"Transform 10k rows took {elapsed:.2f}s (limit: 1.0s)"


@pytest.mark.performance
@pytest.mark.regression
class TestNoPolarsPerformanceWarnings:
    """Verify UOM normalization uses vectorized operations."""

    def test_normalize_uom_10k_rows_under_0_5s(self):
        n_rows = 10_000
        uom_values = ["KG", "LB", "EA", "CT", "OZ", "CS", "PK", "BG"] * (n_rows // 8)

        df = pl.DataFrame({
            "Store": [f"S{i % 10:03d}" for i in range(n_rows)],
            "UPC": [f"{100000 + i}" for i in range(n_rows)],
            "uom_raw": uom_values,
        })

        result = _make_discovery_result(
            columns=["Store", "UPC", "uom_raw"],
            candidate_uom=[CandidateMapping(physical_column="uom_raw", confidence=0.9)],
        )

        start = time.perf_counter()
        normalized = normalize_uom(df, result)
        elapsed = time.perf_counter() - start

        assert normalized is not None
        assert normalized.height == n_rows
        assert "uom" in normalized.columns
        assert elapsed < 0.5, f"UOM normalization took {elapsed:.3f}s (limit: 0.5s)"
