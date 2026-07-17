"""Candidate column detection for canonical mapping."""

from typing import Dict, List, Optional


def detect_candidate_columns(columns: List[str]) -> Dict[str, Optional[str]]:
    """Heuristically propose canonical column mappings from physical column names.

    Returns a dict mapping canonical roles to candidate physical column names:
    store, upc, description, units, price, weight_qty, weight_uom, units_uom.
    """
    candidates: Dict[str, Optional[str]] = {
        "store": None,
        "upc": None,
        "description": None,
        "units": None,
        "price": None,
        "weight_qty": None,
        "weight_uom": None,
        "units_uom": None,
    }

    col_lower = {c: c.lower().strip() for c in columns}

    for phys_col, name in col_lower.items():
        # Store
        if any(kw in name for kw in ["store", "store_nbr", "location", "site", "branch"]):
            candidates["store"] = candidates["store"] or phys_col

        # UPC
        if any(kw in name for kw in ["upc", "sku", "item", "product_code", "plu", "barcode"]):
            candidates["upc"] = candidates["upc"] or phys_col

        # Description
        if any(kw in name for kw in ["desc", "name", "product", "item_desc", "title", "label"]):
            candidates["description"] = candidates["description"] or phys_col

        # Units (quantity count)
        if any(kw in name for kw in ["unit", "qty", "quantity", "count", "sold", "volume"]):
            if "uom" not in name and "weight" not in name and "lb" not in name and "kg" not in name:
                candidates["units"] = candidates["units"] or phys_col

        # Price
        if any(kw in name for kw in ["price", "amount", "total", "sales", "dollar", "revenue", "cost", "ext"]):
            candidates["price"] = candidates["price"] or phys_col

        # Weight quantity
        if any(kw in name for kw in ["weight", "lb", "kg", "pound"]):
            if "uom" not in name:
                candidates["weight_qty"] = candidates["weight_qty"] or phys_col
                if candidates["units"] == phys_col:
                    candidates["units"] = None

        # Weight UOM
        if any(kw in name for kw in ["uom", "measure", "unit_of_measure"]):
            if any(w in name for w in ["weight", "lb", "kg"]):
                candidates["weight_uom"] = candidates["weight_uom"] or phys_col
            else:
                candidates["units_uom"] = candidates["units_uom"] or phys_col

    return candidates
