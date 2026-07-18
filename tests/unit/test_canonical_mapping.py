"""Unit tests for canonical column mapping."""

import pytest

from dav_platform.canonical.mapping import (
    get_canonical_columns,
    get_mapping_dict,
    get_unmapped_columns,
    map_columns,
)
from dav_platform.core.contracts import CandidateMapping, DiscoveryResult, FileType


class TestMapColumns:
    def test_basic_mapping(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["Store_Nbr", "UPC", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store_Nbr", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
        )
        mappings = map_columns(result)
        assert len(mappings) == 3
        mapped = {m.physical_column: m.canonical_name for m in mappings}
        assert mapped["Store_Nbr"] == "store"
        assert mapped["UPC"] == "upc"
        assert mapped["Price"] == "price"

    def test_no_candidates(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["col1", "col2"],
        )
        mappings = map_columns(result)
        assert len(mappings) == 0

    def test_best_candidate_wins(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_store=[
                CandidateMapping(physical_column="Loc", confidence=0.6),
                CandidateMapping(physical_column="Store_Nbr", confidence=0.9),
            ],
        )
        mappings = map_columns(result)
        assert len(mappings) == 1
        assert mappings[0].physical_column == "Store_Nbr"
        assert mappings[0].canonical_name == "store"

    def test_one_to_one_mapping(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_store=[CandidateMapping(physical_column="S1", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="S1", confidence=0.8)],
        )
        mappings = map_columns(result)
        assert len(mappings) == 1  # S1 mapped to best match only


class TestGetMappingDict:
    def test_basic_dict(self):
        from dav_platform.core.contracts import ColumnMapping
        mappings = [
            ColumnMapping(physical_column="A", canonical_name="store", confidence=0.9),
            ColumnMapping(physical_column="B", canonical_name="upc", confidence=0.8),
        ]
        d = get_mapping_dict(mappings)
        assert d == {"A": "store", "B": "upc"}


class TestGetCanonicalColumns:
    def test_ordered_unique(self):
        from dav_platform.core.contracts import ColumnMapping
        mappings = [
            ColumnMapping(physical_column="A", canonical_name="store"),
            ColumnMapping(physical_column="B", canonical_name="upc"),
            ColumnMapping(physical_column="C", canonical_name="store"),
        ]
        cols = get_canonical_columns(mappings)
        assert cols == ["store", "upc"]


class TestGetUnmappedColumns:
    def test_unmapped(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            columns=["A", "B", "C"],
        )
        from dav_platform.core.contracts import ColumnMapping
        mappings = [ColumnMapping(physical_column="A", canonical_name="store")]
        unmapped = get_unmapped_columns(result, mappings)
        assert unmapped == ["B", "C"]
