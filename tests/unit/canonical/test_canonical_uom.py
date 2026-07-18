"""Tests for UOM normalization."""

import pytest
import polars as pl

from dav_platform.canonical.uom import normalize_uom, UOM_MAP
from dav_platform.core.contracts import CandidateMapping, DiscoveryResult, FileType


class TestNormalizeUom:
    def test_normalizes_uom_values(self):
        df = pl.DataFrame({"UOM_COL": ["KG", "lb", "EACH", "unknown"]})
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_uom=[CandidateMapping(physical_column="UOM_COL", confidence=0.9)],
        )
        df = normalize_uom(df, result)
        assert "uom" in df.columns
        assert df["uom"][0] == "KG"
        assert df["uom"][1] == "LB"
        assert df["uom"][2] == "EA"

    def test_default_uom_when_missing(self):
        df = pl.DataFrame({"Other": [1, 2, 3]})
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )
        df = normalize_uom(df, result)
        assert "uom" in df.columns
        assert df["uom"][0] == "EA"

    def test_none_dataframe(self):
        result = DiscoveryResult(file_path="/test.csv", file_type=FileType.DELIMITED)
        df = normalize_uom(None, result)
        assert df is None

    def test_uom_map_coverage(self):
        assert "KG" in UOM_MAP
        assert "LB" in UOM_MAP
        assert "EA" in UOM_MAP
        assert "CT" in UOM_MAP
