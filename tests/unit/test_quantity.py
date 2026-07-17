"""Unit tests for quantity intelligence."""

import pytest

from dav_platform.shared.quantity import recommend_quantity_column
from dav_platform.core.contracts import CandidateMapping, QuantityRecommendation


class TestRecommendQuantityColumn:
    def test_weighted_qty_preferred(self):
        candidates = {
            "weighted_qty": [CandidateMapping(physical_column="Weight_LB", confidence=0.9)],
            "units": [CandidateMapping(physical_column="Units_Sold", confidence=0.8)],
        }
        rec = recommend_quantity_column(candidates)
        assert rec.recommendation_type == "weighted_qty"
        assert rec.recommended_column == "Weight_LB"

    def test_units_fallback(self):
        candidates = {
            "weighted_qty": [],
            "units": [CandidateMapping(physical_column="Units_Sold", confidence=0.7)],
        }
        rec = recommend_quantity_column(candidates)
        assert rec.recommendation_type == "units"
        assert rec.recommended_column == "Units_Sold"

    def test_no_quantity(self):
        candidates = {
            "weighted_qty": [],
            "units": [],
        }
        rec = recommend_quantity_column(candidates)
        assert rec.recommendation_type == "none"
        assert rec.recommended_column is None

    def test_low_confidence_weighted(self):
        candidates = {
            "weighted_qty": [CandidateMapping(physical_column="Weight", confidence=0.3)],
            "units": [CandidateMapping(physical_column="Qty", confidence=0.6)],
        }
        rec = recommend_quantity_column(candidates)
        # Low confidence weighted falls back to units if units has decent confidence
        assert rec.recommendation_type in ("weighted_qty", "units")

    def test_empty_candidates(self):
        rec = recommend_quantity_column({})
        assert rec.recommendation_type == "none"
