"""Quantity intelligence recommendations."""

from typing import Dict, List, Optional

from dav_platform.core.contracts import CandidateMapping, QuantityRecommendation


def recommend_quantity_column(
    candidates: Dict[str, List[CandidateMapping]],
) -> Optional[QuantityRecommendation]:
    """Recommend the best quantity column based on business rules.

    Business Rules:
    - Use Weighted Quantity whenever present
    - Fallback to Units only when:
      - Weighted Quantity column missing OR
      - Weighted Quantity is zero/null AND Units contains value
    """
    weighted = candidates.get("weighted_qty", [])
    units = candidates.get("units", [])

    # Best weighted qty candidate
    best_weighted = weighted[0] if weighted else None
    best_units = units[0] if units else None

    if best_weighted and best_weighted.confidence > 0.5:
        return QuantityRecommendation(
            recommended_column=best_weighted.physical_column,
            recommendation_type="weighted_qty",
            reason="Weighted quantity column detected with high confidence",
            confidence=best_weighted.confidence,
        )

    if best_units and best_units.confidence > 0.3:
        return QuantityRecommendation(
            recommended_column=best_units.physical_column,
            recommendation_type="units",
            reason="Units column detected; no weighted quantity found",
            confidence=best_units.confidence,
        )

    if best_weighted:
        return QuantityRecommendation(
            recommended_column=best_weighted.physical_column,
            recommendation_type="weighted_qty",
            reason="Weighted quantity column detected (low confidence)",
            confidence=best_weighted.confidence,
        )

    return QuantityRecommendation(
        recommended_column=None,
        recommendation_type="none",
        reason="No quantity columns detected",
        confidence=0.0,
    )
