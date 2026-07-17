"""DiscoveryReport generation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import (
    CandidateMapping,
    DiscoveryResult,
    FileType,
    LayoutField,
    RecordTypeInfo,
)


@dataclass
class DiscoveryReport:
    """Human-readable discovery report."""
    file_path: str = ""
    file_type: str = ""
    delimiter: Optional[str] = None
    encoding: str = ""
    has_header: bool = False
    header_prefix: Optional[str] = None
    trailer_prefix: Optional[str] = None
    record_hierarchy: Optional[Dict] = None
    layout_recommendation: List[LayoutField] = field(default_factory=list)
    candidate_columns: Dict[str, List[str]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0
    statistics: Dict[str, Any] = field(default_factory=dict)


def generate_discovery_report(result: DiscoveryResult) -> DiscoveryReport:
    """Generate a DiscoveryReport from a DiscoveryResult."""
    report = DiscoveryReport(
        file_path=result.file_path,
        file_type=result.file_type.value,
        delimiter=result.delimiter,
        encoding=result.encoding,
        has_header=result.has_header,
        header_prefix=result.header_prefix,
        trailer_prefix=result.trailer_prefix,
        record_hierarchy=result.record_hierarchy,
        layout_recommendation=result.layout_fields,
        warnings=result.warnings,
        recommendations=result.recommendations,
        confidence=result.confidence,
    )

    # Convert candidate mappings to simple column name lists
    all_candidates = {
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
        "currency": result.candidate_currency,
        "date": result.candidate_date,
        "time": result.candidate_time,
        "promotion": result.candidate_promotion,
        "store_type": result.candidate_store_type,
        "region": result.candidate_region,
        "division": result.candidate_division,
        "uom": result.candidate_uom,
        "record_type": result.candidate_record_type,
    }

    for role, mappings in all_candidates.items():
        if mappings:
            report.candidate_columns[role] = [m.physical_column for m in mappings]

    # Add statistics
    if result.statistics:
        report.statistics = {
            "estimated_rows": result.statistics.estimated_rows,
            "record_count": result.statistics.record_count,
            "avg_record_length": result.statistics.avg_record_length,
        }

    return report
