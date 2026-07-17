"""Detection Layer — Heart of the platform.

Responsibilities:
- Detect file type (delimited, fixed-width, multiline, Excel)
- Detect delimiter, encoding, header
- Detect record types, prefixes (dynamic, not hardcoded)
- Detect trailer prefix
- Generate layout intelligence (fixed-width)
- Generate candidate column mappings (19 roles)
- Compute confidence scores
- Generate statistics
- Generate previews (raw, flatten)
- Support Excel workbook discovery

Output: DiscoveryResult (ONLY source of truth)
No downstream rediscovery allowed.
"""

from dav_platform.detection.engine import DetectionEngine
from dav_platform.detection.delimiter import detect_delimiter
from dav_platform.detection.header import detect_header
from dav_platform.detection.multiline import detect_multiline, detect_record_types, detect_trailer_prefix
from dav_platform.detection.candidates import detect_candidate_columns
from dav_platform.detection.confidence import compute_confidence_score
from dav_platform.detection.encoding import detect_encoding
from dav_platform.detection.layout import detect_column_breaks, generate_layout_fields
from dav_platform.detection.statistics import collect_statistics
from dav_platform.detection.excel import discover_excel_sheets
from dav_platform.detection.previews import generate_raw_preview, generate_flatten_preview

__all__ = [
    "DetectionEngine",
    "detect_delimiter",
    "detect_header",
    "detect_multiline",
    "detect_record_types",
    "detect_trailer_prefix",
    "detect_candidate_columns",
    "compute_confidence_score",
    "detect_encoding",
    "detect_column_breaks",
    "generate_layout_fields",
    "collect_statistics",
    "discover_excel_sheets",
    "generate_raw_preview",
    "generate_flatten_preview",
]
