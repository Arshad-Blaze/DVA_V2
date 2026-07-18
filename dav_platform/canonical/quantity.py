"""Quantity resolution.

Determines which column represents quantity based on
Detection's recommendation and candidate confidence.
"""

from typing import Optional, Tuple

from dav_platform.core.contracts import DiscoveryResult


def resolve_quantity(result: DiscoveryResult) -> Tuple[Optional[str], str]:
    """Resolve which column represents quantity.

    Returns:
        (column_name, quantity_type)
        quantity_type is "weighted_qty", "units", or "none"
    """
    # Use Detection's recommendation if available
    if result.quantity_recommendation:
        rec = result.quantity_recommendation
        if rec.recommendation_type != "none" and rec.recommended_column:
            return rec.recommended_column, rec.recommendation_type

    # Fallback: check candidates directly
    if result.candidate_weighted_qty:
        return result.candidate_weighted_qty[0].physical_column, "weighted_qty"
    if result.candidate_units:
        return result.candidate_units[0].physical_column, "units"

    return None, "none"


def get_weight_column(result: DiscoveryResult) -> Optional[str]:
    """Get the weight column if available."""
    if result.candidate_weighted_qty:
        return result.candidate_weighted_qty[0].physical_column
    return None


def get_uom_column(result: DiscoveryResult) -> Optional[str]:
    """Get the unit of measure column if available."""
    if result.candidate_uom:
        return result.candidate_uom[0].physical_column
    return None
