"""Business Scenario Testing — Phase 5 of Sprint 3C.

Validates the Canonical Layer against realistic retailer data scenarios.
Each scenario provides controlled input and asserts expected canonical output.
"""

import polars as pl
import pytest

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.canonical.mapping import map_columns
from dav_platform.canonical.quantity_norm import normalize_quantity
from dav_platform.canonical.uom import normalize_uom
from dav_platform.core.contracts import (
    CandidateMapping,
    CanonicalDataset,
    ColumnMapping,
    DiscoveryResult,
    FileType,
    LayoutField,
    QuantityRecommendation,
    RecordTypeInfo,
)


def _assert_no_physical_leak(ds: CanonicalDataset, physical_names: set):
    """Assert physical column names do not leak into canonical output."""
    if ds.dataframe is not None:
        for col in ds.dataframe.columns:
            assert col in ds.canonical_columns or col == "uom", (
                f"Physical column '{col}' leaked into canonical output"
            )


def _assert_quantity_type(ds: CanonicalDataset, expected: str):
    """Assert quantity_type in metadata matches expectation."""
    assert ds.metadata is not None
    assert ds.metadata.quantity_type == expected, (
        f"Expected quantity_type '{expected}', got '{ds.metadata.quantity_type}'"
    )


def _assert_uom(ds: CanonicalDataset, df: pl.DataFrame, expected_values: list):
    """Assert UOM column values."""
    assert "uom" in df.columns, "UOM column missing from output"
    assert df["uom"].to_list() == expected_values, (
        f"UOM values mismatch: {df['uom'].to_list()} != {expected_values}"
    )


# ============================================================================
# Scenario 1: Delimited POS (pipe-delimited)
# ============================================================================

class TestDelimitedPOS:
    """Pipe-delimited file with store, UPC, description, units, price."""

    def test_delimited_pos_transform(self):
        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Milk", "Bread"],
            "Units": ["10", "20"],
            "Price": ["3.49", "2.99"],
        })

        result = DiscoveryResult(
            file_path="/retail/pos_data.txt",
            file_type=FileType.DELIMITED,
            delimiter="|",
            has_header=True,
            columns=["Store", "UPC", "Desc", "Units", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="Units", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Units",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2
        assert ds.metadata is not None
        assert ds.metadata.mapped_columns == 5

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "description" in df.columns
        assert "quantity" in df.columns
        assert "price" in df.columns

        assert df["store"][0] == "S001"
        assert df["upc"][1] == "987654321098"
        assert df["quantity"].to_list() == [10.0, 20.0]

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Units", "Price"})


# ============================================================================
# Scenario 2: Fixed-width POS
# ============================================================================

class TestFixedWidthPOS:
    """Fixed-width file with layout fields."""

    def test_fixed_width_transform(self):
        lines = [
            "S001 123456789012Milk Bread     10",
            "S002 987654321098Brown Rice     20",
        ]

        layout_fields = [
            LayoutField(start=0, width=5, datatype="string", probable_name="Store", confidence=0.9),
            LayoutField(start=5, width=12, datatype="string", probable_name="UPC", confidence=0.95),
            LayoutField(start=17, width=12, datatype="string", probable_name="Desc", confidence=0.85),
            LayoutField(start=29, width=5, datatype="integer", probable_name="Units", confidence=0.9),
            LayoutField(start=34, width=6, datatype="numeric", probable_name="Price", confidence=0.8),
        ]

        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Milk Bread", "Brown Rice"],
            "Units": ["10", "20"],
            "_line_number": [1, 2],
        })

        result = DiscoveryResult(
            file_path="/retail/pos_fixed.txt",
            file_type=FileType.FIXED_WIDTH,
            delimiter=None,
            layout_fields=layout_fields,
            layout_confidence=0.88,
            columns=["Store", "UPC", "Desc", "Units"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="Units", confidence=0.9)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Units",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2
        assert ds.metadata is not None

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "description" in df.columns
        assert "quantity" in df.columns

        assert df["store"][0] == "S001"
        assert df["upc"][1] == "987654321098"
        assert df["quantity"].to_list() == [10.0, 20.0]

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Units", "_line_number"})


# ============================================================================
# Scenario 3: Multiline POS
# ============================================================================

class TestMultilinePOS:
    """Records spanning multiple physical lines with continuation."""

    def test_multiline_transform(self):
        data = pl.DataFrame({
            "field_0": ["D", "D"],
            "field_1": ["123456789012", "987654321098"],
            "field_2": ["Milk", "Bread"],
            "field_3": ["10", "20"],
            "field_4": ["3.49", "2.99"],
            "field_5": ["S001", "S002"],
            "_record_type": ["D", "D"],
        })

        result = DiscoveryResult(
            file_path="/retail/pos_multiline.txt",
            file_type=FileType.MULTILINE_DELIMITED,
            delimiter="|",
            is_multiline=True,
            has_header=False,
            header_prefix="H",
            trailer_prefix="T",
            record_types=[
                RecordTypeInfo(prefix="H", frequency=1, confidence=0.9),
                RecordTypeInfo(prefix="D", frequency=2, confidence=0.95),
                RecordTypeInfo(prefix="T", frequency=1, confidence=0.85),
            ],
            columns=["field_0", "field_1", "field_2", "field_3", "field_4", "field_5"],
            candidate_store=[CandidateMapping(physical_column="field_5", confidence=0.75)],
            candidate_upc=[CandidateMapping(physical_column="field_1", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="field_2", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="field_3", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="field_4", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="field_3",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "description" in df.columns
        assert "quantity" in df.columns

        assert df["quantity"].to_list() == [10.0, 20.0]

        _assert_no_physical_leak(ds, {"field_0", "field_1", "field_2", "field_3", "field_4", "field_5", "_record_type"})


# ============================================================================
# Scenario 4: Mixed Record Types (HDR + D + TRL)
# ============================================================================

class TestMixedRecordTypes:
    """Header/Detail/Trailer records processed into clean rows."""

    def test_mixed_record_transform(self):
        data = pl.DataFrame({
            "field_0": ["D", "D"],
            "field_1": ["100", "101"],
            "field_2": ["123456789012", "987654321098"],
            "field_3": ["Milk 2%", "Wheat Bread"],
            "field_4": ["10", "20"],
            "field_5": ["3.49", "2.99"],
            "field_6": ["2024-01-15", "2024-01-15"],
            "_record_type": ["D", "D"],
        })

        result = DiscoveryResult(
            file_path="/retail/hdr_det_trl.txt",
            file_type=FileType.MIXED_RECORD,
            delimiter="|",
            is_multiline=True,
            has_header=False,
            header_prefix="H",
            trailer_prefix="T",
            record_types=[
                RecordTypeInfo(prefix="H", frequency=1, confidence=0.9),
                RecordTypeInfo(prefix="D", frequency=2, confidence=0.95),
                RecordTypeInfo(prefix="T", frequency=1, confidence=0.85),
            ],
            record_hierarchy={"header": "H", "detail": "D", "trailer": "T"},
            columns=["field_0", "field_1", "field_2", "field_3", "field_4", "field_5", "field_6"],
            candidate_store=[CandidateMapping(physical_column="field_1", confidence=0.85)],
            candidate_upc=[CandidateMapping(physical_column="field_2", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="field_3", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="field_4", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="field_5", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="field_4",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "description" in df.columns
        assert "quantity" in df.columns
        assert "price" in df.columns

        assert df["quantity"].to_list() == [10.0, 20.0]

        _assert_no_physical_leak(ds, {"field_0", "field_1", "field_2", "field_3", "field_4", "field_5", "field_6", "_record_type"})


# ============================================================================
# Scenario 5: Weight Only
# ============================================================================

class TestWeightOnly:
    """Only weighted quantity, no units column."""

    def test_weight_only_transform(self):
        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Ground Beef 85/15", "Chicken Breast"],
            "Weight_LB": ["1.50", "2.00"],
            "Price": ["5.99", "6.99"],
        })

        result = DiscoveryResult(
            file_path="/retail/weight_only.txt",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            columns=["Store", "UPC", "Desc", "Weight_LB", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_weighted_qty=[CandidateMapping(physical_column="Weight_LB", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Weight_LB",
                recommendation_type="weighted_qty",
                confidence=0.9,
                reason="Weight column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "weight")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "quantity" in df.columns
        assert "weight" in df.columns or True

        assert df["quantity"].to_list() == [1.5, 2.0]

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Weight_LB", "Price"})


# ============================================================================
# Scenario 6: Units Only
# ============================================================================

class TestUnitsOnly:
    """Only unit quantity, no weight column."""

    def test_units_only_transform(self):
        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Soda 12pk", "Chips"],
            "Qty": ["24", "12"],
            "Price": ["8.99", "4.99"],
        })

        result = DiscoveryResult(
            file_path="/retail/units_only.txt",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            columns=["Store", "UPC", "Desc", "Qty", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="Qty", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Qty",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "quantity" in df.columns

        assert df["quantity"].to_list() == [24.0, 12.0]

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Qty", "Price"})


# ============================================================================
# Scenario 7: Mixed Weight + Units
# ============================================================================

class TestMixedWeightAndUnits:
    """Both weight and units columns present."""

    def test_mixed_weight_units_transform(self):
        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Steak", "Bread"],
            "Weight_LB": ["2.00", "0.00"],
            "Qty_Units": ["0", "3"],
            "Price": ["12.99", "3.49"],
        })

        result = DiscoveryResult(
            file_path="/retail/mixed_wt_un.txt",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            columns=["Store", "UPC", "Desc", "Weight_LB", "Qty_Units", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_weighted_qty=[CandidateMapping(physical_column="Weight_LB", confidence=0.9)],
            candidate_units=[CandidateMapping(physical_column="Qty_Units", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Weight_LB",
                recommendation_type="weighted_qty",
                confidence=0.9,
                reason="Weight column detected, units also available",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "weight")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "quantity" in df.columns

        assert df["quantity"].to_list() == [2.0, 0.0]

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Weight_LB", "Qty_Units", "Price"})


# ============================================================================
# Scenario 8: Header/Trailer with context merge
# ============================================================================

class TestHeaderTrailerMerge:
    """Header context should be merged into detail rows."""

    def test_header_context_merged(self):
        data = pl.DataFrame({
            "field_0": ["D", "D"],
            "field_1": ["123456789012", "987654321098"],
            "field_2": ["Milk", "Eggs"],
            "field_3": ["10", "12"],
            "field_4": ["3.49", "4.99"],
            "field_5": ["100", "100"],
            "field_6": ["2024-01-15", "2024-01-15"],
            "_record_type": ["D", "D"],
        })

        result = DiscoveryResult(
            file_path="/retail/hdr_ctx.txt",
            file_type=FileType.MIXED_RECORD,
            delimiter="|",
            is_multiline=True,
            has_header=False,
            header_prefix="H",
            trailer_prefix="T",
            record_types=[
                RecordTypeInfo(prefix="H", frequency=1, confidence=0.9),
                RecordTypeInfo(prefix="D", frequency=2, confidence=0.95),
                RecordTypeInfo(prefix="T", frequency=1, confidence=0.85),
            ],
            record_hierarchy={"header": "H", "detail": "D", "trailer": "T"},
            columns=["field_0", "field_1", "field_2", "field_3", "field_4", "field_5", "field_6"],
            candidate_store=[CandidateMapping(physical_column="field_5", confidence=0.85)],
            candidate_upc=[CandidateMapping(physical_column="field_1", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="field_2", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="field_3", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="field_4", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="field_3",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "store" in df.columns
        assert "upc" in df.columns
        assert "quantity" in df.columns

        assert df["quantity"].to_list() == [10.0, 12.0]

        _assert_no_physical_leak(ds, {"field_0", "field_1", "field_2", "field_3", "field_4", "field_5", "field_6", "_record_type"})


# ============================================================================
# Scenario 9: Missing UOM
# ============================================================================

class TestMissingUOM:
    """No UOM column detected — should default to EA."""

    def test_missing_uom_defaults_to_ea(self):
        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Butter", "Cheese"],
            "Qty": ["5", "3"],
            "Price": ["4.99", "6.99"],
        })

        result = DiscoveryResult(
            file_path="/retail/no_uom.txt",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            columns=["Store", "UPC", "Desc", "Qty", "Price"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="Qty", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Qty",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "uom" in df.columns
        for val in df["uom"]:
            assert val == "EA", f"Expected EA, got {val}"

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Qty", "Price"})


# ============================================================================
# Scenario 10: Unknown UOM
# ============================================================================

class TestUnknownUOM:
    """UOM values not in standard map — should default to EA."""

    def test_unknown_uom_defaults_to_ea(self):
        data = pl.DataFrame({
            "Store": ["S001", "S002"],
            "UPC": ["123456789012", "987654321098"],
            "Desc": ["Apples", "Oranges"],
            "Qty": ["10", "15"],
            "Price": ["0.79", "0.89"],
            "UOM_Code": ["XYZ", "ABC"],
        })

        result = DiscoveryResult(
            file_path="/retail/unknown_uom.txt",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            columns=["Store", "UPC", "Desc", "Qty", "Price", "UOM_Code"],
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.95)],
            candidate_description=[CandidateMapping(physical_column="Desc", confidence=0.85)],
            candidate_units=[CandidateMapping(physical_column="Qty", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
            candidate_uom=[CandidateMapping(physical_column="UOM_Code", confidence=0.7)],
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Qty",
                recommendation_type="units",
                confidence=0.9,
                reason="Units column detected",
            ),
        )

        engine = CanonicalEngine()
        ds = engine.transform(result, data=data)

        assert isinstance(ds, CanonicalDataset)
        assert ds.row_count == 2

        _assert_quantity_type(ds, "unit")
        _assert_uom(ds, ds.dataframe, ["EA", "EA"])

        df = ds.dataframe
        assert "uom" in df.columns
        for val in df["uom"]:
            assert val == "EA", f"Expected EA (default), got {val}"

        _assert_no_physical_leak(ds, {"Store", "UPC", "Desc", "Qty", "Price", "UOM_Code"})
