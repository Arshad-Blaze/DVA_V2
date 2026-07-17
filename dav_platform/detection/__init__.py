"""Detection Layer - Heart of the platform.

Responsibilities:
- Detect file type (delimited, fixed-width, multiline, Excel)
- Detect delimiter, encoding, header
- Detect record types, prefixes
- Generate previews (raw, flatten, canonical)
- Compute confidence scores
- Generate warnings and recommendations

Output: DiscoveryResult (ONLY source of truth)
No downstream rediscovery allowed.
"""

from dav_platform.detection.engine import DetectionEngine
from dav_platform.detection.delimiter import detect_delimiter
from dav_platform.detection.header import detect_header
from dav_platform.detection.multiline import detect_multiline, detect_record_types, detect_trailer_prefix
from dav_platform.detection.candidates import detect_candidate_columns
from dav_platform.detection.confidence import compute_confidence_score

__all__ = [
    "DetectionEngine",
    "detect_delimiter",
    "detect_header",
    "detect_multiline",
    "detect_record_types",
    "detect_trailer_prefix",
    "detect_candidate_columns",
    "compute_confidence_score",
]
