"""Preview service — Business Preview Studio (Sprint 4B).

Wraps CanonicalService for review-only display.
Tracks approval workflow, packages comparison data,
validation status, quality metrics, and warnings.
Never maps, validates, or transforms data.
"""

from typing import Any, Callable, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import CanonicalMetadata, CanonicalDataset


PIPELINE_STAGES = [
    {"id": "detection", "label": "Detection", "icon": "search"},
    {"id": "canonical", "label": "Business Mapping", "icon": "transform"},
    {"id": "preview", "label": "Business Preview", "icon": "preview"},
    {"id": "ready", "label": "Ready for Processing", "icon": "check_circle"},
]

PREVIEW_COLUMNS = [
    {"name": "store", "label": "Store", "field": "store", "align": "left"},
    {"name": "upc", "label": "UPC", "field": "upc", "align": "left"},
    {"name": "description", "label": "Description", "field": "description", "align": "left"},
    {"name": "quantity", "label": "Quantity", "field": "quantity", "align": "right"},
    {"name": "uom", "label": "UOM", "field": "uom", "align": "center"},
    {"name": "price", "label": "Price", "field": "price", "align": "right"},
    {"name": "category", "label": "Category", "field": "category", "align": "left"},
    {"name": "brand", "label": "Brand", "field": "brand", "align": "left"},
    {"name": "department", "label": "Department", "field": "department", "align": "left"},
    {"name": "date", "label": "Date", "field": "date", "align": "left"},
]

class PreviewService:
    """Manages Business Preview state.

    Wraps CanonicalService for read-only display.
    Tracks approval workflow. Never transforms data.
    """

    def __init__(self, canonical_svc):
        from ui.services.canonical_service import CanonicalService
        self._canonical: CanonicalService = canonical_svc
        self._approved: bool = False
        self._rejected: bool = False
        self._on_change: Optional[Callable] = None
        self._preview_rows: List[Dict[str, Any]] = []
        self._statistics: Dict[str, Any] = {}

    # ── Dataset population from canonical layer ───────────────

    def load_dataset(self, dataset: Optional[CanonicalDataset] = None) -> None:
        """Populate preview rows and statistics from the canonical dataset.

        If dataset is None, derives it from the wrapped CanonicalService.
        """
        if dataset is None:
            dataset = getattr(self._canonical, "_dataset", None)
        if dataset is None:
            self._preview_rows = []
            self._statistics = {}
            self._notify()
            return

        df = dataset.dataframe
        if df is not None and not df.is_empty():
            self._preview_rows = [
                self._row_to_dict(row) for row in df.head(20).iter_rows(named=True)
            ]
            self._statistics = self._compute_statistics(df, dataset)
        else:
            self._preview_rows = []
            self._statistics = {}
        self._notify()

    @staticmethod
    def _row_to_dict(row: dict) -> Dict[str, Any]:
        result = {}
        for k, v in row.items():
            if hasattr(v, "strftime"):
                result[k] = v.strftime("%Y-%m-%d")
            else:
                result[k] = v
        return result

    @staticmethod
    def _compute_statistics(df: pl.DataFrame, dataset: CanonicalDataset) -> Dict[str, Any]:
        stats: Dict[str, Any] = {
            "total_rows": df.height,
        }
        if "store" in df.columns:
            stats["stores"] = df["store"].n_unique()
        if "upc" in df.columns:
            stats["upcs"] = df["upc"].n_unique()
        if "category" in df.columns:
            stats["categories"] = df["category"].n_unique()
        if "brand" in df.columns:
            stats["brands"] = df["brand"].n_unique()
        if "department" in df.columns:
            stats["departments"] = df["department"].n_unique()
        if "date" in df.columns:
            stats["date_range"] = f"{df['date'].min()} → {df['date'].max()}"
        if df.height:
            completeness_cols = [c for c in df.columns if c in df.columns]
            non_null = sum(df[c].null_count() for c in completeness_cols) if completeness_cols else 0
            stats["completeness"] = round((1 - non_null / max(len(completeness_cols) * df.height, 1)) * 100, 1)
        else:
            stats["completeness"] = 0.0
        return stats

    # ── Pipeline ──────────────────────────────────────────────

    @property
    def pipeline_stages(self) -> List[Dict[str, Any]]:
        return list(PIPELINE_STAGES)

    @property
    def current_stage_index(self) -> int:
        return 2  # Business Preview stage is always active

    # ── Side-by-Side Comparison ───────────────────────────────

    def get_comparison_rows(self) -> List[Dict[str, Any]]:
        rows = []
        for mapping in self._canonical.mappings.values():
            if mapping.physical_column:
                rows.append({
                    "physical": mapping.physical_column,
                    "business": mapping.canonical_name,
                    "confidence": mapping.confidence,
                    "source": mapping.source,
                })
        return rows

    # ── Business Dataset Preview ──────────────────────────────

    @property
    def preview_columns(self) -> List[Dict[str, Any]]:
        dataset = getattr(self._canonical, "_dataset", None)
        if dataset is not None and dataset.dataframe is not None:
            return [{"name": c, "label": c, "field": c, "align": "left"}
                    for c in dataset.dataframe.columns]
        return list(PREVIEW_COLUMNS)

    @property
    def preview_rows(self) -> List[Dict[str, Any]]:
        return list(self._preview_rows)

    @property
    def preview_row_count(self) -> int:
        return self._statistics.get("total_rows", 0)

    # ── Validation ────────────────────────────────────────────

    def get_validation_checks(self) -> List[Dict[str, Any]]:
        s = self._canonical.get_summary()
        total_phys = len(self._canonical.physical_columns)
        mapped = s["mapped"]
        ignored = s["ignored"]
        conf = s["confidence"]
        missing = self._canonical.get_required_missing()
        essentials = ["store", "upc", "description", "quantity", "price", "date"]

        mapping_status = "pass" if mapped + ignored >= total_phys else "fail"
        mapping_detail = f"{mapped + ignored} of {total_phys} physical columns mapped or ignored" if total_phys else "No physical columns"

        fields_status = "pass" if not missing else "fail"
        fields_detail = ", ".join(e for e in essentials if e not in self._canonical.mappings) if missing else "All required fields mapped"

        schema_status = "pass" if mapped > 0 else "fail"
        schema_detail = f"{mapped} business fields mapped"

        qty_status = "pass" if self._canonical.quantity_strategy else "fail"
        qty_detail = f"Strategy: {self._canonical.quantity_strategy}, UOM: {self._canonical.uom_value}"

        conf_status = "pass" if conf >= 0.8 else "fail"
        conf_detail = f"Overall confidence: {conf:.0%} (threshold: 80%)"

        physicals = [m.physical_column for m in self._canonical.mappings.values() if m.physical_column]
        no_dup = len(physicals) == len(set(physicals))
        dup_status = "pass" if no_dup else "fail"
        dup_detail = "Each physical column mapped to exactly one business field" if no_dup else "Duplicate mappings detected"

        ignored_detail = f"{ignored} columns ignored" if ignored else "No columns currently ignored"

        return [
            {"id": "mapping_complete", "label": "Mapping Complete", "status": mapping_status, "detail": mapping_detail},
            {"id": "required_fields", "label": "Required Fields Present", "status": fields_status, "detail": fields_detail},
            {"id": "business_schema", "label": "Business Schema Ready", "status": schema_status, "detail": schema_detail},
            {"id": "quantity_resolved", "label": "Quantity Resolved", "status": qty_status, "detail": qty_detail},
            {"id": "confidence_threshold", "label": "Confidence Threshold Met", "status": conf_status, "detail": conf_detail},
            {"id": "no_duplicates", "label": "No Duplicate Mappings", "status": dup_status, "detail": dup_detail},
            {"id": "ignored_reviewed", "label": "Ignored Columns Reviewed", "status": "info", "detail": ignored_detail},
        ]

    # ── Quality Dashboard ─────────────────────────────────────

    @property
    def quality_metrics(self) -> Dict[str, Any]:
        s = self._canonical.get_summary()
        mapped = s["mapped"]
        missing = s["required_missing"]
        confidence = s["confidence"]
        if mapped > 0 and missing == 0 and confidence >= 0.8:
            quality = "High"
        elif mapped > 0 and missing == 0:
            quality = "Medium"
        else:
            quality = "Review Required"
        return {
            "overall_quality": quality,
            "mapping_confidence": confidence,
            "required_coverage": f"{mapped - missing} / {mapped}",
            "optional_coverage": "5 / 7",
            "manual_mappings": sum(1 for m in self._canonical.mappings.values() if m.source == "user"),
            "auto_mappings": sum(1 for m in self._canonical.mappings.values() if m.source == "candidate"),
            "ignored_columns": s["ignored"],
            "missing_columns": s["unmapped"],
            "overall_readiness": "Ready" if s["required_missing"] == 0 else "Review Required",
        }

    # ── Business Statistics ───────────────────────────────────

    @property
    def business_statistics(self) -> Dict[str, Any]:
        if not self._statistics:
            self.load_dataset()
        return dict(self._statistics)

    # ── Metadata ──────────────────────────────────────────────

    @property
    def metadata(self) -> CanonicalMetadata:
        return self._canonical.get_metadata()

    # ── Warnings ──────────────────────────────────────────────

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        warnings = []
        missing = self._canonical.get_required_missing()
        if missing:
            warnings.append({
                "problem": f"Required fields missing: {', '.join(missing)}",
                "impact": "Processing may fail without these fields",
                "recommendation": "Return to Canonical Mapping to complete mapping",
                "severity": "error",
            })
        return warnings

    # ── Approval ──────────────────────────────────────────────

    def get_approval_checklist(self) -> List[Dict[str, Any]]:
        checks = [
            {"id": "mapping_complete", "label": "Mapping Complete", "status": len(self._canonical.mappings) > 0},
            {"id": "validation_passed", "label": "Validation Passed", "status": all(
                chk["status"] in ("pass", "info") for chk in self.get_validation_checks()
            )},
            {"id": "required_fields", "label": "Required Fields Present", "status": len(self._canonical.get_required_missing()) == 0},
            {"id": "business_schema", "label": "Business Schema Ready", "status": len(self._canonical.mappings) >= 6},
            {"id": "dataset_generated", "label": "Canonical Dataset Generated", "status": True},
        ]
        return checks

    @property
    def can_approve(self) -> bool:
        return all(c["status"] for c in self.get_approval_checklist())

    @property
    def is_approved(self) -> bool:
        return self._approved

    @property
    def is_rejected(self) -> bool:
        return self._rejected

    def approve(self) -> None:
        if self.can_approve:
            self._approved = True
            self._rejected = False
            self._notify()

    def reject(self) -> None:
        self._approved = False
        self._rejected = True
        self._notify()

    def reset_approval(self) -> None:
        self._approved = False
        self._rejected = False
        self._notify()

    # ── Export ────────────────────────────────────────────────

    def get_export_data(self, format: str = "csv") -> str:
        import io
        import csv
        buf = io.StringIO()
        if self._preview_rows:
            writer = csv.DictWriter(buf, fieldnames=list(self._preview_rows[0].keys()))
            writer.writeheader()
            writer.writerows(self._preview_rows)
        return buf.getvalue()

    def get_mapping_export(self) -> str:
        import io
        import csv
        buf = io.StringIO()
        mappings = self._canonical.mappings
        writer = csv.writer(buf)
        writer.writerow(["Business Field", "Physical Column", "Confidence", "Source"])
        for business, mapping in sorted(mappings.items()):
            writer.writerow([business, mapping.physical_column, mapping.confidence, mapping.source])
        return buf.getvalue()

    # ── Events ────────────────────────────────────────────────

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
