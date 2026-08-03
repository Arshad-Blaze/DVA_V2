"""Discovery Report — presentation layer for detection results.

Moved from detection/ to avoid layer violation.
Detection detects; reporting presents.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dav_platform.core.contracts import (
    DiscoveryResult,
)


@dataclass
class DiscoveryReport:
    """Formatted report for UI/console display."""
    file_path: str = ""
    file_type: str = ""
    delimiter: Optional[str] = None
    encoding: str = "utf-8"
    has_header: bool = True
    is_multiline: bool = False
    confidence: float = 0.0
    columns: List[str] = field(default_factory=list)
    record_types: List[str] = field(default_factory=list)
    candidate_columns: Dict[str, List[str]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


def generate_discovery_report(result: DiscoveryResult) -> DiscoveryReport:
    """Convert DiscoveryResult to display-friendly report."""
    candidate_columns = {}
    role_map = {
        "store": result.candidate_store,
        "upc": result.candidate_upc,
        "description": result.candidate_description,
        "brand": result.candidate_brand,
        "department": result.candidate_department,
        "category": result.candidate_category,
        "units": result.candidate_units,
        "weighted_qty": result.candidate_weighted_qty,
        "price": result.candidate_price,
        "sales": result.candidate_sales,
    }

    for role, candidates in role_map.items():
        if candidates:
            candidate_columns[role] = [c.physical_column for c in candidates]

    return DiscoveryReport(
        file_path=result.file_path,
        file_type=result.file_type.value,
        delimiter=result.delimiter,
        encoding=result.encoding,
        has_header=result.has_header,
        is_multiline=result.is_multiline,
        confidence=result.confidence,
        columns=result.columns or [],
        record_types=[rt.prefix for rt in result.record_types],
        candidate_columns=candidate_columns,
        warnings=result.warnings,
        recommendations=result.recommendations,
    )
