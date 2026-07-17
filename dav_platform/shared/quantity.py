"""Quantity Intelligence — recommends which quantity column to use.

Moved from detection/ to avoid business logic in detection layer.
Detection detects candidates; this recommends strategy.
"""

from typing import Dict, List

from dav_platform.core.contracts import CandidateMapping, QuantityRecommendation


def recommend_quantity_column(
    candidates: Dict[str, List[CandidateMapping]],
) -> QuantityRecommendation:
    """Recommend which quantity column to use for calculations.

    Priority:
    1. Weighted quantity (if high confidence)
    2. Units (fallback)
    3. None
    """
    weighted = candidates.get("weighted_qty", [])
    units = candidates.get("units", [])

    # Prefer weighted if confidence is reasonable
    if weighted and weighted[0].confidence >= 0.5:
        return QuantityRecommendation(
            recommendation_type="weighted_qty",
            recommended_column=weighted[0].physical_column,
            confidence=weighted[0].confidence,
            reason="Weighted quantity column detected with sufficient confidence",
        )

    # Fallback to units
    if units:
        return QuantityRecommendation(
            recommendation_type="units",
            recommended_column=units[0].physical_column,
            confidence=units[0].confidence,
            reason="Using units column as quantity source",
        )

    return QuantityRecommendation(
        recommendation_type="none",
        recommended_column=None,
        confidence=0.0,
        reason="No quantity columns detected",
    )
