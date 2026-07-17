"""Candidate column detection for canonical mapping.

Supports 19 business roles with confidence scores.
"""

from typing import Dict, List

from dav_platform.core.contracts import CandidateMapping


# Keyword groups for each canonical role
ROLE_KEYWORDS: Dict[str, List[str]] = {
    "store": ["store", "store_nbr", "location", "site", "branch", "store_id", "loc"],
    "upc": ["upc", "sku", "item", "product_code", "plu", "barcode", "item_nbr", "prod"],
    "description": ["desc", "name", "product", "item_desc", "title", "label", "prod_desc"],
    "brand": ["brand", "brand_name", "mfr", "manufacturer"],
    "department": ["dept", "department", "dept_nbr", "dept_id"],
    "category": ["category", "cat", "cat_nbr", "class", "subcat"],
    "units": ["unit", "qty", "quantity", "count", "sold", "volume", "units_sold"],
    "weighted_qty": ["weight", "lb", "kg", "pound", "weighted", "wtd_qty", "weight_qty"],
    "price": ["price", "amount", "total", "sales", "dollar", "revenue", "cost", "ext", "unit_price"],
    "sales": ["sales", "revenue", "total_sales", "ext_price", "extended", "net_sales"],
    "currency": ["currency", "curr", "cur", "currency_code"],
    "date": ["date", "dt", "trans_date", "sale_date", "txn_date", "effect_date"],
    "time": ["time", "tm", "trans_time", "sale_time", "txn_time"],
    "promotion": ["promo", "promotion", "deal", "discount", "offer"],
    "store_type": ["store_type", "type", "format", "store_format", "store_class"],
    "region": ["region", "area", "district", "territory", "zone"],
    "division": ["division", "div", "div_nbr", "business_unit"],
    "uom": ["uom", "measure", "unit_of_measure", "uom_desc"],
    "record_type": ["record_type", "rec_type", "type", "prefix", "line_type"],
}


def detect_candidate_columns(columns: List[str]) -> Dict[str, List[CandidateMapping]]:
    """Detect candidate column mappings for all 19 business roles.

    Returns:
        Dict mapping role name to list of CandidateMapping (sorted by confidence).
    """
    candidates: Dict[str, List[CandidateMapping]] = {role: [] for role in ROLE_KEYWORDS}

    col_lower = {c: c.lower().strip() for c in columns}

    for phys_col, name in col_lower.items():
        for role, keywords in ROLE_KEYWORDS.items():
            confidence = _compute_keyword_match_confidence(name, keywords)
            if confidence > 0:
                candidates[role].append(CandidateMapping(
                    physical_column=phys_col,
                    confidence=confidence,
                ))

    # Sort each role's candidates by confidence descending
    for role in candidates:
        candidates[role].sort(key=lambda c: c.confidence, reverse=True)

    return candidates


def _compute_keyword_match_confidence(name: str, keywords: List[str]) -> float:
    """Compute match confidence between a column name and keyword list.

    Returns 0.0 if no match, otherwise 0.3-1.0 based on match quality.
    """
    for kw in keywords:
        if kw == name:
            return 1.0  # Exact match
        if kw in name:
            # Partial match - longer keyword relative to name = higher confidence
            ratio = len(kw) / max(len(name), 1)
            return max(0.3, min(0.9, 0.5 + ratio * 0.4))
    return 0.0
