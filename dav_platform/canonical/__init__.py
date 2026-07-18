"""Canonical Layer — Business data standardization.

Responsibilities:
- Map physical columns to canonical names
- Resolve quantity (weighted_qty, units, none)
- Normalize quantity and UOM
- Flatten hierarchies and multiline records
- Transform fixed-width data
- Build business schema
- Validate before data leaves the layer
- Generate canonical preview
- Support streaming for large files

Input: DiscoveryResult (from Detection Layer)
Output: CanonicalDataset (to Requirement/Processing layers)

Detection is FROZEN. This layer consumes its output.
After this layer, no downstream layer knows about retailer formats.
"""

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.canonical.mapping import map_columns
from dav_platform.canonical.quantity import resolve_quantity
from dav_platform.canonical.quantity_norm import normalize_quantity
from dav_platform.canonical.uom import normalize_uom
from dav_platform.canonical.schema import build_business_schema
from dav_platform.canonical.validation import validate_canonical

__all__ = [
    "CanonicalEngine",
    "map_columns",
    "resolve_quantity",
    "normalize_quantity",
    "normalize_uom",
    "build_business_schema",
    "validate_canonical",
]
