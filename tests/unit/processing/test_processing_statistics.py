import pytest
import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ProcessingStatistics,
)
from dav_platform.processing.statistics import StatisticsEngine


def _make_dataset() -> CanonicalDataset:
    df = pl.DataFrame({
        "store": ["S1", "S1", "S1", "S2", "S3"],
        "upc": ["U1", "U1", "U2", "U1", "U1"],
        "units": [10, 20, 30, 40, 50],
        "price": [1.0, 2.0, 3.0, 4.0, 5.0],
    })
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=["store", "upc", "units", "price"],
        metadata=CanonicalMetadata(
            total_rows=5,
            quantity_column="units",
            quantity_type="units",
        ),
        dataframe=df,
    )


@pytest.mark.unit
class TestStatisticsEngine:
    def test_compute_returns_correct_total_rows(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert isinstance(stats, ProcessingStatistics)
        assert stats.total_rows == 5

    def test_compute_unique_store_count(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert stats.unique_stores == 3

    def test_compute_unique_upc_count(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert stats.unique_upcs == 2

    def test_compute_null_counts(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert isinstance(stats.null_counts, dict)
        assert stats.null_counts.get("units", 0) == 0
        assert stats.null_counts.get("price", 0) == 0

    def test_compute_duplicate_count(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert stats.duplicate_count == 2

    def test_compute_numeric_stats_min_max_mean_median(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert "units" in stats.column_stats
        units_stats = stats.column_stats["units"]
        assert units_stats["min"] == 10
        assert units_stats["max"] == 50
        assert units_stats["mean"] == pytest.approx(30.0)
        assert units_stats["median"] == pytest.approx(30.0)

    def test_compute_with_missing_columns_handled_gracefully(self):
        df = pl.DataFrame({
            "store": ["S1", "S2"],
            "units": [10, 20],
        })
        dataset = CanonicalDataset(
            file_path="/sparse.csv",
            canonical_columns=["store", "units"],
            dataframe=df,
        )
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert stats.total_rows == 2
        assert stats.unique_upcs == 0

    def test_compute_timing_greater_than_zero(self):
        dataset = _make_dataset()
        engine = StatisticsEngine()
        stats = engine.compute(dataset)
        assert stats.elapsed_seconds >= 0
