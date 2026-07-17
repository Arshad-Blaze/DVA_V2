"""Detection Engine - Main entry point for file detection.

This is the ONLY source of truth for file structure.
No downstream layer may re-detect.
"""

import os
from typing import Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import (
    IDataSource,
    DiscoveryResult,
    FileType,
)
from dav_platform.detection.delimiter import detect_delimiter, validate_delimiter_consistency
from dav_platform.detection.header import detect_header, detect_header_prefix
from dav_platform.detection.multiline import (
    detect_multiline,
    detect_record_types,
    detect_trailer_prefix,
)
from dav_platform.detection.candidates import detect_candidate_columns
from dav_platform.detection.confidence import compute_confidence_score


class DetectionEngine:
    """Orchestrates all detection heuristics.

    Consumes IDataSource and produces DiscoveryResult.
    """

    def __init__(self, source: IDataSource):
        self.source = source

    def detect(self, file_path: str) -> DiscoveryResult:
        """Run all detection heuristics and return consolidated result.

        This is the single detection entry point that fully describes a file.
        """
        file_type, delimiter, scores = self._detect_file_type(file_path)
        multiline = self._detect_multiline(file_path) if file_type else False

        result = DiscoveryResult(
            file_path=file_path,
            file_type=file_type or FileType.UNKNOWN,
            delimiter=delimiter,
            has_header=False,
            is_multiline=multiline,
        )

        # Store delimiter scores for confidence calculation
        result_dict: Dict = {
            "file_path": file_path,
            "file_type": file_type.value if file_type else None,
            "delimiter": delimiter,
            "is_multiline": multiline,
            "has_header": False,
            "header_prefix": None,
            "trailer_prefix": None,
            "ml_record_types": None,
            "_delimiter_scores": scores,
        }

        if file_type is None:
            result.warnings.append("File type could not be determined")
            result.recommendations.append(
                "Verify the file format is supported (delimited, fixed-width, multiline, or Excel)"
            )
            result.confidence = 0.0
            return result

        if file_type == FileType.EXCEL:
            result.confidence = 1.0
            return result

        # Fixed-width files need manual layout configuration
        if file_type == FileType.FIXED_WIDTH:
            result.warnings.append("Fixed-width file detected — manual layout configuration required")
            result.recommendations.append("Use Layout Builder to define field positions")

        # Delimiter consistency check
        if file_type == FileType.DELIMITED and delimiter:
            lines = self._read_sample_lines(file_path, 5)
            consistency = validate_delimiter_consistency(lines, delimiter)
            if consistency < 0.8:
                result.warnings.append(f"Delimiter '{delimiter}' has low consistency: {consistency}")

        # Multiline detection
        if multiline:
            lines = self._read_sample_lines(file_path, 20)
            hdr_prefix = detect_header_prefix(lines)
            if hdr_prefix:
                result.header_prefix = hdr_prefix
                result_dict["header_prefix"] = hdr_prefix

            record_types = detect_record_types(lines, delimiter=delimiter)
            if record_types:
                result.record_types = record_types
                result_dict["ml_record_types"] = record_types

            trailer = detect_trailer_prefix(lines)
            if trailer:
                result.trailer_prefix = trailer
            else:
                result.warnings.append("No trailer prefix detected")
                result.recommendations.append(
                    "If the file has trailer records, set trailer_prefix manually"
                )

        # Header detection
        if file_type == FileType.DELIMITED and delimiter:
            lines = self._read_sample_lines(file_path, 1)
            result.has_header = detect_header(lines, delimiter=delimiter)
            result_dict["has_header"] = result.has_header
            if not result.has_header:
                result.warnings.append("No header row detected — columns will be auto-named")
                result.recommendations.append(
                    "Consider adding a header row or configuring column names"
                )

        # Columns detection
        if file_type == FileType.DELIMITED and delimiter:
            columns = self._detect_columns(file_path, delimiter)
            result.columns = columns

            if columns:
                candidates = detect_candidate_columns(columns)
                result.candidate_quantity_columns = [c for c in [candidates.get("units")] if c]
                result.candidate_price_columns = [c for c in [candidates.get("price")] if c]
                result.candidate_uom_columns = [
                    c for c in [candidates.get("weight_uom"), candidates.get("units_uom")] if c
                ]

        # Confidence score
        result_dict["has_header"] = result.has_header
        result.confidence = compute_confidence_score(result_dict)

        return result

    def _detect_file_type(self, file_path: str):
        """Detect file type and delimiter."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in (".xlsx", ".xls"):
                return FileType.EXCEL, None, {}

            lines = self._read_sample_lines(file_path, 5)
            lines = [l for l in lines if l]

            delimiter, scores = detect_delimiter(lines)

            if delimiter:
                return FileType.DELIMITED, delimiter, scores
            return FileType.FIXED, None, {}
        except Exception:
            return None, None, {}

    def _detect_multiline(self, file_path: str) -> bool:
        """Detect if file uses multiline records."""
        try:
            lines = self._read_sample_lines(file_path, 10)
            return detect_multiline(lines)
        except Exception:
            return False

    def _detect_columns(self, file_path: str, delimiter: str) -> List[str]:
        """Detect column names from header row."""
        try:
            lines = self._read_sample_lines(file_path, 1)
            if not lines:
                return []
            first_line = lines[0].strip()
            if not first_line:
                return []
            return [col.strip() for col in first_line.split(delimiter)]
        except Exception:
            return []

    def _read_sample_lines(self, file_path: str, n: int) -> List[str]:
        """Read n lines from file via data source."""
        try:
            raw = self.source.read_sample(file_path, n=n)
            return [line.rstrip("\n\r") for line in raw.splitlines()]
        except Exception:
            return []
