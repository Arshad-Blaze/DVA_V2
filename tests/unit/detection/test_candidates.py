"""Unit tests for candidate column detection."""

import pytest

from dav_platform.detection.candidates import detect_candidate_columns


class TestDetectCandidateColumns:
    def test_store_column(self):
        columns = ["Store_Nbr", "Product", "Price"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["store"]) > 0
        assert candidates["store"][0].physical_column == "Store_Nbr"

    def test_upc_column(self):
        columns = ["UPC_Code", "Description", "Quantity"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["upc"]) > 0
        assert candidates["upc"][0].physical_column == "UPC_Code"

    def test_description_column(self):
        columns = ["Item_Desc", "Price", "Qty"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["description"]) > 0
        assert candidates["description"][0].physical_column == "Item_Desc"

    def test_units_column(self):
        columns = ["Units_Sold", "Revenue"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["units"]) > 0
        assert candidates["units"][0].physical_column == "Units_Sold"

    def test_price_column(self):
        columns = ["Unit_Price", "Total_Sales"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["price"]) > 0
        assert candidates["price"][0].physical_column == "Unit_Price"

    def test_weight_column(self):
        columns = ["Weight_LB", "Price"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["weighted_qty"]) > 0
        assert candidates["weighted_qty"][0].physical_column == "Weight_LB"

    def test_uom_column(self):
        columns = ["Weight_UOM", "Price"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["uom"]) > 0
        assert candidates["uom"][0].physical_column == "Weight_UOM"

    def test_no_matches(self):
        columns = ["Col1", "Col2", "Col3"]
        candidates = detect_candidate_columns(columns)
        assert all(len(v) == 0 for v in candidates.values())

    def test_empty_columns(self):
        candidates = detect_candidate_columns([])
        assert all(len(v) == 0 for v in candidates.values())

    def test_multiple_candidates(self):
        columns = ["Store_Nbr", "Store_ID", "Location"]
        candidates = detect_candidate_columns(columns)
        assert len(candidates["store"]) >= 2

    def test_confidence_scores(self):
        columns = ["store", "upc", "price"]
        candidates = detect_candidate_columns(columns)
        for role, mappings in candidates.items():
            for m in mappings:
                assert 0.0 <= m.confidence <= 1.0
