"""Tests for canonical validation."""

import pytest
import polars as pl

from dav_platform.canonical.validation import validate_canonical, validate_mapping_completeness
from dav_platform.core.contracts import CanonicalDataset, ColumnMapping, CanonicalMetadata


class TestValidateCanonical:
    def test_valid_dataset(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            physical_to_canonical={"A": "store", "B": "upc"},
            column_mappings=[
                ColumnMapping(physical_column="A", canonical_name="store"),
                ColumnMapping(physical_column="B", canonical_name="upc"),
            ],
            dataframe=pl.DataFrame({"A": [1], "B": ["x"]}),
            metadata=CanonicalMetadata(total_rows=1),
        )
        result = validate_canonical(ds)
        assert result.passed is True

    def test_empty_dataset(self):
        ds = CanonicalDataset(file_path="/test.csv")
        result = validate_canonical(ds)
        assert result.passed is True
        assert len(result.warnings) > 0

    def test_duplicate_mappings(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            column_mappings=[
                ColumnMapping(physical_column="A", canonical_name="store"),
                ColumnMapping(physical_column="B", canonical_name="store"),
            ],
            dataframe=pl.DataFrame({"A": [1], "B": [2]}),
        )
        result = validate_canonical(ds)
        assert result.passed is False

    def test_missing_mandatory_columns(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            column_mappings=[
                ColumnMapping(physical_column="A", canonical_name="description"),
            ],
            dataframe=pl.DataFrame({"A": ["x"]}),
        )
        result = validate_canonical(ds)
        assert len(result.warnings) > 0

    def test_mapped_column_not_in_dataframe(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            column_mappings=[
                ColumnMapping(physical_column="MissingCol", canonical_name="store"),
            ],
            dataframe=pl.DataFrame({"A": [1]}),
        )
        result = validate_canonical(ds)
        assert any("not in DataFrame" in w for w in result.warnings)

    def test_empty_dataframe(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            column_mappings=[
                ColumnMapping(physical_column="A", canonical_name="store"),
            ],
            dataframe=pl.DataFrame({"A": []}),
        )
        result = validate_canonical(ds)
        assert result.passed is True
        assert any("empty" in w.lower() for w in result.warnings)

    def test_physical_in_dict_not_in_mappings(self):
        ds = CanonicalDataset(
            file_path="/test.csv",
            physical_to_canonical={"A": "store", "B": "upc"},
            column_mappings=[
                ColumnMapping(physical_column="A", canonical_name="store"),
            ],
            dataframe=pl.DataFrame({"A": [1], "B": [2]}),
        )
        result = validate_canonical(ds)
        assert any("mapping dict but not in mappings" in w for w in result.warnings)


class TestValidateMappingCompleteness:
    def test_complete_mapping(self):
        mappings = [
            ColumnMapping(physical_column="A", canonical_name="store"),
            ColumnMapping(physical_column="B", canonical_name="upc"),
        ]
        result = validate_mapping_completeness(mappings, 2)
        assert result.passed is True

    def test_no_mappings(self):
        result = validate_mapping_completeness([], 5)
        assert result.passed is False

    def test_low_coverage(self):
        mappings = [ColumnMapping(physical_column="A", canonical_name="store")]
        result = validate_mapping_completeness(mappings, 20)
        assert len(result.warnings) > 0
