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
