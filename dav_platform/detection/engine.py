"""Detection Engine — Main orchestrator for enterprise file detection.

This is the ONLY source of truth for file structure.
No downstream layer may re-detect.
"""

import os
from typing import Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import (
    IDataSource,
    CandidateMapping,
    DiscoveryResult,
    EncodingType,
    ExcelSheetInfo,
    FileType,
    LayoutField,
    RecordTypeInfo,
)
from dav_platform.detection.candidates import detect_candidate_columns
from dav_platform.detection.confidence import compute_confidence_score
from dav_platform.detection.context import DiscoveryContext
from dav_platform.detection.delimiter import detect_delimiter, validate_delimiter_consistency
from dav_platform.detection.encoding import detect_encoding
from dav_platform.detection.excel import discover_excel_sheets, select_candidate_sheet
from dav_platform.detection.header import detect_header, detect_header_prefix
from dav_platform.detection.layout import detect_column_breaks, generate_layout_fields
from dav_platform.detection.multiline import (
    build_record_hierarchy,
    detect_multiline,
    detect_record_types,
    detect_record_types_detailed,
    detect_trailer_prefix,
)
from dav_platform.detection.previews import (
    generate_canonical_preview,
    generate_flatten_preview,
    generate_raw_preview,
)
from dav_platform.detection.quantity import recommend_quantity_column
from dav_platform.detection.statistics import collect_statistics


class DetectionEngine:
    """Orchestrates all detection heuristics.

    Consumes IDataSource and produces DiscoveryResult.
    Runs exactly once per file.
    """

    def __init__(self, source: IDataSource):
        self.source = source

    def detect(self, file_path: str) -> DiscoveryResult:
        """Run ALL detection heuristics and return consolidated result.

        This is the single entry point that fully describes a file.
        Downstream layers MUST consume this result instead of re-detecting.
        """
        # Build internal context
        ctx = self._build_context(file_path)

        # Detect file type
        file_type, delimiter, scores = self._detect_file_type(file_path, ctx)

        # Initialize result
        result = DiscoveryResult(
            file_path=file_path,
            file_type=file_type or FileType.UNKNOWN,
            delimiter=delimiter,
        )

        if file_type is None:
            result.warnings.append("File type could not be determined")
            result.recommendations.append(
                "Verify the file format is supported"
            )
            result.confidence = 0.0
            return result

        # Encoding detection
        if ctx.raw_sample:
            raw_bytes = ctx.raw_sample.encode('utf-8', errors='replace')
            enc_type, enc_conf = detect_encoding(raw_bytes)
            result.encoding_type = enc_type
            result.encoding = enc_type.value
            result.encoding_confidence = enc_conf

        # Excel handling
        if file_type == FileType.EXCEL:
            return self._detect_excel(file_path, result)

        # Delimited or Fixed-width processing
        if file_type in (FileType.DELIMITED, FileType.MULTILINE_DELIMITED):
            self._detect_delimited(ctx, result, delimiter, scores)
        elif file_type in (FileType.FIXED_WIDTH, FileType.FIXED_WIDTH_MULTILINE):
            self._detect_fixed_width(ctx, result)

        # Multiline detection (applies to both types)
        multiline = detect_multiline(ctx.non_empty_lines)
        result.is_multiline = multiline

        if multiline:
            self._detect_multiline_details(ctx, result)

        # Statistics
        result.statistics = collect_statistics(ctx.non_empty_lines, delimiter)

        # Candidate columns
        if result.columns:
            all_candidates = detect_candidate_columns(result.columns)
            self._map_candidates(result, all_candidates)

        # Quantity intelligence
        qty_candidates = {
            "weighted_qty": result.candidate_weighted_qty,
            "units": result.candidate_units,
        }
        result.quantity_recommendation = recommend_quantity_column(qty_candidates)

        # Previews
        result.raw_preview = generate_raw_preview(ctx.non_empty_lines)
        if result.columns or result.record_types:
            result.flatten_preview = generate_flatten_preview(
                ctx.non_empty_lines,
                result.delimiter,
                result.file_type,
                result.record_types,
                result.layout_fields,
                result.header_prefix,
                result.trailer_prefix,
            )
        if result.flatten_preview is not None:
            candidate_dict = {
                "store": result.candidate_store,
                "upc": result.candidate_upc,
                "description": result.candidate_description,
                "price": result.candidate_price,
                "units": result.candidate_units,
            }
            result.canonical_preview = generate_canonical_preview(
                result.flatten_preview, candidate_dict
            )

        # Overall confidence
        result_dict = {
            "file_type": result.file_type.value,
            "delimiter": result.delimiter,
            "_delimiter_scores": scores,
            "is_multiline": result.is_multiline,
            "header_prefix": result.header_prefix,
            "ml_record_types": [rt.prefix for rt in result.record_types],
            "has_header": result.has_header,
            "trailer_prefix": result.trailer_prefix,
        }
        result.confidence = compute_confidence_score(result_dict)
        result.delimiter_confidence = scores.get(delimiter, 0) / max(sum(scores.values()), 1) if scores and delimiter else 0.0
        result.header_confidence = 1.0 if result.has_header else 0.0

        return result

    def _build_context(self, file_path: str) -> DiscoveryContext:
        """Build internal discovery context."""
        ctx = DiscoveryContext()
        try:
            ctx.raw_sample = self.source.read_sample(file_path, n=200)
            ctx.lines = [line.rstrip("\n\r") for line in ctx.raw_sample.splitlines()]
            ctx.non_empty_lines = [l for l in ctx.lines if l.strip()]
            ctx.total_lines = len(ctx.lines)
            ctx.blank_lines = ctx.total_lines - len(ctx.non_empty_lines)
            ctx.data_lines = len(ctx.non_empty_lines)

            if ctx.non_empty_lines:
                lengths = [len(l) for l in ctx.non_empty_lines]
                ctx.avg_line_length = sum(lengths) / len(lengths)
                ctx.min_line_length = min(lengths)
                ctx.max_line_length = max(lengths)
        except Exception:
            pass
        return ctx

    def _detect_file_type(self, file_path: str, ctx: DiscoveryContext):
        """Detect file type and delimiter."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in (".xlsx", ".xls"):
                return FileType.EXCEL, None, {}

            lines = ctx.non_empty_lines[:5]
            delimiter, scores = detect_delimiter(lines)

            if delimiter:
                return FileType.DELIMITED, delimiter, scores
            return FileType.FIXED_WIDTH, None, {}
        except Exception:
            return None, None, {}

    def _detect_delimited(
        self,
        ctx: DiscoveryContext,
        result: DiscoveryResult,
        delimiter: str,
        scores: dict,
    ) -> None:
        """Detect properties specific to delimited files."""
        # Header detection
        lines = ctx.non_empty_lines[:1]
        result.has_header = detect_header(lines, delimiter=delimiter)

        # Column detection
        if result.has_header and ctx.non_empty_lines:
            first_line = ctx.non_empty_lines[0].strip()
            result.columns = [col.strip() for col in first_line.split(delimiter)]

        # Multiline check
        multiline = detect_multiline(ctx.non_empty_lines[:10])
        result.is_multiline = multiline

    def _detect_fixed_width(self, ctx: DiscoveryContext, result: DiscoveryResult) -> None:
        """Detect properties specific to fixed-width files."""
        result.warnings.append("Fixed-width file detected")
        result.recommendations.append("Use Layout Builder to define field positions")

        # Layout intelligence
        breaks = detect_column_breaks(ctx.non_empty_lines)
        if breaks:
            result.layout_fields = generate_layout_fields(
                ctx.non_empty_lines, breaks
            )
            result.layout_confidence = sum(f.confidence for f in result.layout_fields) / max(len(result.layout_fields), 1)

    def _detect_multiline_details(self, ctx: DiscoveryContext, result: DiscoveryResult) -> None:
        """Detect multiline-specific properties."""
        lines = ctx.non_empty_lines

        # Record types (detailed)
        result.record_types = detect_record_types_detailed(lines, result.delimiter)

        # Header prefix
        hdr_prefix = detect_header_prefix(lines)
        if hdr_prefix:
            result.header_prefix = hdr_prefix

        # Trailer prefix
        trailer = detect_trailer_prefix(lines)
        if trailer:
            result.trailer_prefix = trailer
        else:
            result.warnings.append("No trailer prefix detected")
            result.recommendations.append(
                "If the file has trailer records, set trailer_prefix manually"
            )

        # Record hierarchy
        result.record_hierarchy = build_record_hierarchy(result.record_types, lines)

    def _detect_excel(self, file_path: str, result: DiscoveryResult) -> DiscoveryResult:
        """Handle Excel file detection."""
        sheets = discover_excel_sheets(file_path)
        result.excel_sheets = sheets
        result.candidate_sheet = select_candidate_sheet(sheets)
        result.confidence = 1.0 if sheets else 0.0

        if result.candidate_sheet:
            for sheet in sheets:
                if sheet.name == result.candidate_sheet:
                    result.columns = sheet.columns
                    result.has_header = sheet.has_header
                    break

        # Candidate columns for Excel
        if result.columns:
            all_candidates = detect_candidate_columns(result.columns)
            self._map_candidates(result, all_candidates)

        return result

    def _map_candidates(
        self,
        result: DiscoveryResult,
        all_candidates: Dict[str, List[CandidateMapping]],
    ) -> None:
        """Map candidate columns to result fields."""
        role_map = {
            "store": "candidate_store",
            "upc": "candidate_upc",
            "description": "candidate_description",
            "brand": "candidate_brand",
            "department": "candidate_department",
            "category": "candidate_category",
            "units": "candidate_units",
            "weighted_qty": "candidate_weighted_qty",
            "price": "candidate_price",
            "sales": "candidate_sales",
            "currency": "candidate_currency",
            "date": "candidate_date",
            "time": "candidate_time",
            "promotion": "candidate_promotion",
            "store_type": "candidate_store_type",
            "region": "candidate_region",
            "division": "candidate_division",
            "uom": "candidate_uom",
            "record_type": "candidate_record_type",
        }

        for role, field_name in role_map.items():
            if role in all_candidates:
                setattr(result, field_name, all_candidates[role])
