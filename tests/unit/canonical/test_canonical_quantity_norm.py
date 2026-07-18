"""Tests for quantity normalization."""

import pytest
import polars as pl

from dav_platform.canonical.quantity_norm import normalize_quantity
from dav_platform.core.contracts import CandidateMapping, DiscoveryResult, FileType


class TestNormalizeQuantity:
    def test_weight_preferred(self):
        df = pl.DataFrame({
            "Weight_LB": [1.5, 2.0, 0.0],
            "Units_Sold": [10, 20, 30],
        })
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_weighted_qty=[CandidateMapping(physical_column="Weight_LB", confidence=0.9)],
            candidate_units=[CandidateMapping(physical_column="Units_Sold", confidence=0.8)],
        )
        df, col, qty_type = normalize_quantity(df, result)
        assert qty_type == "weight"
        assert "quantity" in df.columns

    def test_units_fallback(self):
        df = pl.DataFrame({
            "Units_Sold": [10, 20, 30],
        })
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_units=[CandidateMapping(physical_column="Units_Sold", confidence=0.8)],
        )
        df, col, qty_type = normalize_quantity(df, result)
        assert qty_type == "unit"

    def test_no_quantity(self):
        df = pl.DataFrame({"Other": [1, 2, 3]})
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )
        df, col, qty_type = normalize_quantity(df, result)
        assert qty_type == "none"
        assert df["quantity"][0] == 0.0

    def test_none_dataframe(self):
        result = DiscoveryResult(file_path="/test.csv", file_type=FileType.DELIMITED)
        df, col, qty_type = normalize_quantity(None, result)
        assert df is None
        assert qty_type == "none"

    def test_empty_dataframe(self):
        df = pl.DataFrame()
        result = DiscoveryResult(file_path="/test.csv", file_type=FileType.DELIMITED)
        df, col, qty_type = normalize_quantity(df, result)
        assert qty_type == "none"
