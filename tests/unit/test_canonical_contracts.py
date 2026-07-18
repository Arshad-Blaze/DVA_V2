"""Unit tests for canonical contracts."""

import pytest

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ColumnMapping,
    CANONICAL_COLUMNS,
)


class TestCanonicalDataset:
    def test_creation(self):
        ds = CanonicalDataset(file_path="/test.csv")
        assert ds.file_path == "/test.csv"
        assert ds.row_count == 0
        assert ds.column_count == 0

    def test_empty_mappings(self):
        ds = CanonicalDataset()
        assert len(ds.column_mappings) == 0
        assert len(ds.physical_to_canonical) == 0


class TestCanonicalMetadata:
    def test_defaults(self):
        m = CanonicalMetadata()
        assert m.total_rows == 0
        assert m.quantity_type == "none"
        assert m.confidence == 0.0


class TestColumnMapping:
    def test_creation(self):
        cm = ColumnMapping(
            physical_column="Store_Nbr",
            canonical_name="store",
            confidence=0.9,
        )
        assert cm.physical_column == "Store_Nbr"
        assert cm.canonical_name == "store"


class TestCanonicalColumns:
    def test_all_defined(self):
        assert "store" in CANONICAL_COLUMNS
        assert "upc" in CANONICAL_COLUMNS
        assert "quantity" in CANONICAL_COLUMNS
        assert "price" in CANONICAL_COLUMNS
