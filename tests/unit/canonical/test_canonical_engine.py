"""Unit tests for canonical engine."""

import pytest

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.core.contracts import (
    CandidateMapping,
    CanonicalDataset,
    DiscoveryResult,
    FileType,
    QuantityRecommendation,
)


class TestCanonicalEngine:
    def test_basic_transform(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            delimiter=",",
            columns=["Store", "UPC", "Price"],
            has_header=True,
            confidence=0.95,
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
        )

        engine = CanonicalEngine()
        ds = engine.transform(result)

        assert isinstance(ds, CanonicalDataset)
        assert ds.file_path == "/test.csv"
        assert len(ds.column_mappings) == 3
        assert ds.metadata is not None
        assert ds.metadata.mapped_columns == 3

    def test_quantity_resolution(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Weight_LB",
                recommendation_type="weighted_qty",
                confidence=0.9,
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result)

        assert ds.metadata.quantity_column == "Weight_LB"
        assert ds.metadata.quantity_type == "weighted_qty"

    def test_no_mappings(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        engine = CanonicalEngine()
        ds = engine.transform(result)

        assert len(ds.column_mappings) == 0
        assert len(ds.recommendations) > 0  # Should recommend manual mapping

    def test_with_data(self):
        import polars as pl
        data = pl.DataFrame({
            "Store": [1, 2, 3],
            "UPC": ["A", "B", "C"],
            "Price": [1.0, 2.0, 3.0],
        })

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["Store", "UPC", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert ds.dataframe is not None
        assert ds.row_count == 3

    def test_transform_with_none_data(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["Store", "UPC"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=None)

        assert ds.dataframe is None
        assert ds.metadata.total_rows == 0
        assert ds.metadata.validation_summary is not None
        assert ds.metadata.validation_summary["passed"] is True

    def test_transform_with_empty_data(self):
        import polars as pl
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["Store", "UPC"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=pl.DataFrame({"Store": [], "UPC": []}))

        assert ds.metadata.total_rows == 0

    def test_validation_summary_populated(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["Store", "UPC", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
        )

        engine = CanonicalEngine()
        ds = engine.transform(result)

        vs = ds.metadata.validation_summary
        assert vs is not None
        assert "passed" in vs
        assert "issues" in vs
        assert "warnings" in vs
        assert "checked_columns" in vs
        assert "total_rows" in vs

    def test_streaming_transform(self):
        import polars as pl

        def chunks():
            yield pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
            yield pl.DataFrame({"A": [3], "B": ["z"]})

        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )

        engine = CanonicalEngine()
        datasets = list(engine.transform_streaming(chunks(), result))
        assert len(datasets) == 2
