"""Unit tests for candidate column detection."""

import pytest

from dav_platform.detection.candidates import detect_candidate_columns


class TestDetectCandidateColumns:
    def test_store_column(self):
        columns = ["Store_Nbr", "Product", "Price"]
        candidates = detect_candidate_columns(columns)
        assert candidates["store"] == "Store_Nbr"

    def test_upc_column(self):
        columns = ["UPC_Code", "Description", "Quantity"]
        candidates = detect_candidate_columns(columns)
        assert candidates["upc"] == "UPC_Code"

    def test_description_column(self):
        columns = ["Item_Desc", "Price", "Qty"]
        candidates = detect_candidate_columns(columns)
        assert candidates["description"] == "Item_Desc"

    def test_units_column(self):
        columns = ["Units_Sold", "Revenue"]
        candidates = detect_candidate_columns(columns)
        assert candidates["units"] == "Units_Sold"

    def test_price_column(self):
        columns = ["Unit_Price", "Total_Sales"]
        candidates = detect_candidate_columns(columns)
        assert candidates["price"] == "Unit_Price"

    def test_weight_column(self):
        columns = ["Weight_LB", "Price"]
        candidates = detect_candidate_columns(columns)
        assert candidates["weight_qty"] == "Weight_LB"

    def test_uom_column(self):
        columns = ["Weight_UOM", "Price"]
        candidates = detect_candidate_columns(columns)
        assert candidates["weight_uom"] == "Weight_UOM"

    def test_no_matches(self):
        columns = ["Col1", "Col2", "Col3"]
        candidates = detect_candidate_columns(columns)
        assert all(v is None for v in candidates.values())

    def test_empty_columns(self):
        candidates = detect_candidate_columns([])
        assert all(v is None for v in candidates.values())
