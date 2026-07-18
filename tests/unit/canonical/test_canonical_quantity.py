"""Unit tests for quantity resolution."""

import pytest

from dav_platform.canonical.quantity import resolve_quantity
from dav_platform.core.contracts import (
    CandidateMapping,
    DiscoveryResult,
    FileType,
    QuantityRecommendation,
)


class TestResolveQuantity:
    def test_uses_recommendation(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            quantity_recommendation=QuantityRecommendation(
                recommended_column="Weight_LB",
                recommendation_type="weighted_qty",
                confidence=0.9,
            ),
        )
        col, qty_type = resolve_quantity(result)
        assert col == "Weight_LB"
        assert qty_type == "weighted_qty"

    def test_fallback_to_weighted_qty(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_weighted_qty=[
                CandidateMapping(physical_column="Weight", confidence=0.7)
            ],
        )
        col, qty_type = resolve_quantity(result)
        assert col == "Weight"
        assert qty_type == "weighted_qty"

    def test_fallback_to_units(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_units=[
                CandidateMapping(physical_column="Qty", confidence=0.6)
            ],
        )
        col, qty_type = resolve_quantity(result)
        assert col == "Qty"
        assert qty_type == "units"

    def test_no_quantity(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
        )
        col, qty_type = resolve_quantity(result)
        assert col is None
        assert qty_type == "none"

    def test_recommendation_none_type(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            quantity_recommendation=QuantityRecommendation(
                recommendation_type="none",
            ),
            candidate_units=[
                CandidateMapping(physical_column="Qty", confidence=0.6)
            ],
        )
        col, qty_type = resolve_quantity(result)
        assert col == "Qty"
        assert qty_type == "units"
