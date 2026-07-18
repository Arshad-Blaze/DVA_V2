"""Tests for business schema builder."""

import pytest

from dav_platform.canonical.schema import build_business_schema, get_schema_info, BUSINESS_SCHEMA_ORDER
from dav_platform.core.contracts import ColumnMapping, DiscoveryResult, FileType


class TestBuildBusinessSchema:
    def test_with_mappings(self):
        mappings = [
            ColumnMapping(physical_column="Store", canonical_name="store"),
            ColumnMapping(physical_column="UPC", canonical_name="upc"),
            ColumnMapping(physical_column="Price", canonical_name="price"),
        ]
        schema = build_business_schema(mappings)
        assert schema == ["store", "upc", "price"]

    def test_empty_mappings(self):
        schema = build_business_schema([])
        assert schema == []

    def test_ordering(self):
        mappings = [
            ColumnMapping(physical_column="P", canonical_name="price"),
            ColumnMapping(physical_column="S", canonical_name="store"),
            ColumnMapping(physical_column="U", canonical_name="upc"),
        ]
        schema = build_business_schema(mappings)
        assert schema == ["store", "upc", "price"]

    def test_all_canonical_columns(self):
        mappings = [ColumnMapping(physical_column=f"p_{c}", canonical_name=c) for c in BUSINESS_SCHEMA_ORDER]
        schema = build_business_schema(mappings)
        assert schema == BUSINESS_SCHEMA_ORDER


class TestGetSchemaInfo:
    def test_basic_info(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["A", "B", "C"],
        )
        mappings = [
            ColumnMapping(physical_column="A", canonical_name="store"),
            ColumnMapping(physical_column="B", canonical_name="upc"),
        ]
        info = get_schema_info(result, mappings)
        assert info["mapped_count"] == "2"
        assert info["unmapped_count"] == "1"
