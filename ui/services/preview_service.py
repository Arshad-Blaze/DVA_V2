"""Preview service — Business Preview Studio (Sprint 4B).

Wraps CanonicalService for review-only display.
Tracks approval workflow, packages comparison data,
validation status, quality metrics, and warnings.
Never maps, validates, or transforms data.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

from dav_platform.core.contracts import CANONICAL_COLUMNS, ColumnMapping, CanonicalMetadata


PIPELINE_STAGES = [
    {"id": "detection", "label": "Detection", "icon": "search"},
    {"id": "canonical", "label": "Business Mapping", "icon": "transform"},
    {"id": "preview", "label": "Business Preview", "icon": "preview"},
    {"id": "ready", "label": "Ready for Processing", "icon": "check_circle"},
]

COMPARISON_ROWS_DEMO = [
    {"physical": "Store", "sample": "S001", "business": "store", "business_sample": "S001", "conf": 0.99, "source": "Auto"},
    {"physical": "UPC", "sample": "490123456789", "business": "upc", "business_sample": "490123456789", "conf": 0.99, "source": "Auto"},
    {"physical": "Description", "sample": "Organic Whole Milk", "business": "description", "business_sample": "Organic Whole Milk", "conf": 0.99, "source": "Auto"},
    {"physical": "Category", "sample": "Dairy", "business": "category", "business_sample": "Dairy", "conf": 0.95, "source": "Auto"},
    {"physical": "Units", "sample": "2", "business": "quantity", "business_sample": "2", "conf": 0.90, "source": "Auto"},
    {"physical": "Price", "sample": "4.99", "business": "price", "business_sample": "4.99", "conf": 0.99, "source": "Auto"},
    {"physical": "Sales", "sample": "9.98", "business": "sales", "business_sample": "9.98", "conf": 0.99, "source": "Auto"},
    {"physical": "Date", "sample": "2026-01-15", "business": "date", "business_sample": "2026-01-15", "conf": 0.99, "source": "Auto"},
    {"physical": "Promotion", "sample": "No", "business": "promotion", "business_sample": "No", "conf": 0.85, "source": "Auto"},
]

PREVIEW_COLUMNS = [
    {"name": "store", "label": "Store", "field": "store", "align": "left"},
    {"name": "upc", "label": "UPC", "field": "upc", "align": "left"},
    {"name": "description", "label": "Description", "field": "description", "align": "left"},
    {"name": "quantity", "label": "Quantity", "field": "quantity", "align": "right"},
    {"name": "uom", "label": "UOM", "field": "uom", "align": "center"},
    {"name": "sales", "label": "Sales", "field": "sales", "align": "right"},
    {"name": "price", "label": "Price", "field": "price", "align": "right"},
    {"name": "category", "label": "Category", "field": "category", "align": "left"},
    {"name": "brand", "label": "Brand", "field": "brand", "align": "left"},
    {"name": "department", "label": "Department", "field": "department", "align": "left"},
    {"name": "date", "label": "Date", "field": "date", "align": "left"},
]

PREVIEW_ROWS_DEMO = [
    {"store": "S001", "upc": "490123456789", "description": "Organic Whole Milk", "quantity": 2, "uom": "each", "sales": 9.98, "price": 4.99, "category": "Dairy", "brand": "Organic Valley", "department": "Dairy", "date": "2026-01-15"},
    {"store": "S001", "upc": "490123456790", "description": "Sourdough Bread", "quantity": 1, "uom": "each", "sales": 5.49, "price": 5.49, "category": "Bakery", "brand": "Artisan Bakes", "department": "Bakery", "date": "2026-01-15"},
    {"store": "S001", "upc": "490123456791", "description": "Bananas Bunch", "quantity": 3, "uom": "lb", "sales": 1.77, "price": 0.59, "category": "Produce", "brand": "Fresh Farms", "department": "Produce", "date": "2026-01-15"},
    {"store": "S001", "upc": "490123456792", "description": "Chicken Breast 1lb", "quantity": 2, "uom": "lb", "sales": 13.98, "price": 6.99, "category": "Meat", "brand": "Premium Meats", "department": "Meat", "date": "2026-01-15"},
    {"store": "S002", "upc": "490123456793", "description": "Greek Yogurt 32oz", "quantity": 1, "uom": "each", "sales": 6.49, "price": 6.49, "category": "Dairy", "brand": "Organic Valley", "department": "Dairy", "date": "2026-01-15"},
    {"store": "S002", "upc": "490123456794", "description": "Cheddar Cheese Block", "quantity": 1, "uom": "each", "sales": 7.99, "price": 7.99, "category": "Dairy", "brand": "Kerrygold", "department": "Dairy", "date": "2026-01-16"},
    {"store": "S002", "upc": "490123456795", "description": "Sparkling Water 12pk", "quantity": 2, "uom": "each", "sales": 9.98, "price": 4.99, "category": "Beverages", "brand": "LaCroix", "department": "Beverages", "date": "2026-01-16"},
    {"store": "S002", "upc": "490123456796", "description": "Paper Towels 6pk", "quantity": 1, "uom": "each", "sales": 8.99, "price": 8.99, "category": "Household", "brand": "Bounty", "department": "Household", "date": "2026-01-16"},
    {"store": "S003", "upc": "490123456797", "description": "Organic Baby Spinach", "quantity": 1, "uom": "each", "sales": 3.99, "price": 3.99, "category": "Produce", "brand": "Fresh Farms", "department": "Produce", "date": "2026-01-16"},
    {"store": "S003", "upc": "490123456798", "description": "Ground Beef 80/20", "quantity": 3, "uom": "lb", "sales": 14.97, "price": 4.99, "category": "Meat", "brand": "Premium Meats", "department": "Meat", "date": "2026-01-17"},
    {"store": "S003", "upc": "490123456799", "description": "Salsa Medium 16oz", "quantity": 2, "uom": "each", "sales": 7.98, "price": 3.99, "category": "Condiments", "brand": "Pace", "department": "Grocery", "date": "2026-01-17"},
    {"store": "S003", "upc": "490123456800", "description": "Tortilla Chips 13oz", "quantity": 2, "uom": "each", "sales": 9.98, "price": 4.99, "category": "Snacks", "brand": "Tostitos", "department": "Grocery", "date": "2026-01-17"},
    {"store": "S001", "upc": "490123456801", "description": "Coca-Cola 12pk", "quantity": 3, "uom": "each", "sales": 14.97, "price": 4.99, "category": "Beverages", "brand": "Coca-Cola", "department": "Beverages", "date": "2026-01-18"},
    {"store": "S001", "upc": "490123456802", "description": "Avocados 4pk", "quantity": 2, "uom": "each", "sales": 7.98, "price": 3.99, "category": "Produce", "brand": "Fresh Farms", "department": "Produce", "date": "2026-01-18"},
    {"store": "S004", "upc": "490123456803", "description": "Frozen Pizza Supreme", "quantity": 2, "uom": "each", "sales": 11.98, "price": 5.99, "category": "Frozen", "brand": "DiGiorno", "department": "Frozen", "date": "2026-01-18"},
    {"store": "S004", "upc": "490123456804", "description": "Ice Cream Vanilla 1qt", "quantity": 1, "uom": "each", "sales": 5.49, "price": 5.49, "category": "Frozen", "brand": "Ben & Jerry's", "department": "Frozen", "date": "2026-01-19"},
    {"store": "S004", "upc": "490123456805", "description": "Dog Food 15lb", "quantity": 1, "uom": "each", "sales": 24.99, "price": 24.99, "category": "Pet", "brand": "Purina", "department": "Pet", "date": "2026-01-19"},
    {"store": "S001", "upc": "490123456806", "description": "Laundry Detergent 50oz", "quantity": 1, "uom": "each", "sales": 12.99, "price": 12.99, "category": "Household", "brand": "Tide", "department": "Household", "date": "2026-01-19"},
    {"store": "S002", "upc": "490123456807", "description": "Orange Juice 64oz", "quantity": 2, "uom": "each", "sales": 9.98, "price": 4.99, "category": "Beverages", "brand": "Tropicana", "department": "Beverages", "date": "2026-01-20"},
    {"store": "S005", "upc": "490123456808", "description": "Butter Unsalted 1lb", "quantity": 2, "uom": "each", "sales": 9.98, "price": 4.99, "category": "Dairy", "brand": "Kerrygold", "department": "Dairy", "date": "2026-01-20"},
]

BUSINESS_STATISTICS_DEMO = {
    "total_rows": 1250,
    "total_columns": 11,
    "stores": 45,
    "unique_upcs": 892,
    "categories": 12,
    "brands": 64,
    "departments": 8,
    "date_range": "2026-01-01 to 2026-03-31",
    "null_pct": 2.1,
    "duplicate_pct": 0.3,
    "completeness": 97.9,
}

WARNINGS_DEMO = [
    {"problem": "Low mapping confidence on Promotion", "impact": "Promotion flag may be inaccurate", "recommendation": "Verify promotion column values", "severity": "warning"},
    {"problem": "Quantity column 'Units' uses count, not weight", "impact": "Weight-based calculations unavailable", "recommendation": "Use weighted_qty if product weights vary", "severity": "info"},
]

VALIDATION_CHECKS_DEMO = [
    {"id": "mapping_complete", "label": "Mapping Complete", "status": "pass", "detail": "All 9 physical columns mapped or ignored"},
    {"id": "required_fields", "label": "Required Fields Present", "status": "pass", "detail": "store, upc, description, quantity, sales, date all mapped"},
    {"id": "business_schema", "label": "Business Schema Ready", "status": "pass", "detail": "11 business fields in canonical dataset"},
    {"id": "quantity_resolved", "label": "Quantity Resolved", "status": "pass", "detail": f"Strategy: units, UOM: each"},
    {"id": "confidence_threshold", "label": "Confidence Threshold Met", "status": "pass", "detail": "Overall confidence: 96% (threshold: 80%)"},
    {"id": "no_duplicates", "label": "No Duplicate Mappings", "status": "pass", "detail": "Each physical column mapped to exactly one business field"},
    {"id": "ignored_reviewed", "label": "Ignored Columns Reviewed", "status": "info", "detail": "No columns currently ignored"},
]

APPROVAL_CHECKLIST_DEMO = [
    {"id": "mapping_complete", "label": "Mapping Complete", "status": False},
    {"id": "validation_passed", "label": "Validation Passed", "status": False},
    {"id": "required_fields", "label": "Required Fields Present", "status": False},
    {"id": "business_schema", "label": "Business Schema Ready", "status": False},
    {"id": "dataset_generated", "label": "Canonical Dataset Generated", "status": False},
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
        self._preview_rows: List[Dict[str, Any]] = list(PREVIEW_ROWS_DEMO)
        self._statistics: Dict[str, Any] = dict(BUSINESS_STATISTICS_DEMO)

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
        for c in COMPARISON_ROWS_DEMO:
            ignored = c["physical"] in self._canonical.ignored_physical
            mapped = c["physical"] in self._canonical.get_mapped_physical()
            if mapped or ignored:
                rows.append(dict(c))
        return rows

    # ── Business Dataset Preview ──────────────────────────────

    @property
    def preview_columns(self) -> List[Dict[str, Any]]:
        return list(PREVIEW_COLUMNS)

    @property
    def preview_rows(self) -> List[Dict[str, Any]]:
        return list(self._preview_rows)

    @property
    def preview_row_count(self) -> int:
        return self._statistics.get("total_rows", 0)

    # ── Validation ────────────────────────────────────────────

    def get_validation_checks(self) -> List[Dict[str, Any]]:
        checks = []
        for c in VALIDATION_CHECKS_DEMO:
            check = dict(c)
            if check["id"] == "quantity_resolved":
                check["detail"] = f"Strategy: {self._canonical.quantity_strategy}, UOM: {self._canonical.uom_value}"
            if check["id"] == "confidence_threshold":
                conf = self._canonical.get_summary()["confidence"]
                check["detail"] = f"Overall confidence: {conf:.0%} (threshold: 80%)"
            if check["id"] == "ignored_reviewed":
                ignored = self._canonical.ignored_physical
                check["detail"] = f"{len(ignored)} columns ignored" if ignored else "No columns currently ignored"
            checks.append(check)
        return checks

    # ── Quality Dashboard ─────────────────────────────────────

    @property
    def quality_metrics(self) -> Dict[str, Any]:
        s = self._canonical.get_summary()
        return {
            "overall_quality": "High",
            "mapping_confidence": s["confidence"],
            "required_coverage": f"{s['mapped'] - s['required_missing']} / {s['mapped']}",
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
        return dict(self._statistics)

    # ── Metadata ──────────────────────────────────────────────

    @property
    def metadata(self) -> CanonicalMetadata:
        return self._canonical.get_metadata()

    # ── Warnings ──────────────────────────────────────────────

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        base = [dict(w) for w in WARNINGS_DEMO]
        missing = self._canonical.get_required_missing()
        if missing:
            base.insert(0, {
                "problem": f"Required fields missing: {', '.join(missing)}",
                "impact": "Processing may fail without these fields",
                "recommendation": "Return to Canonical Mapping to complete mapping",
                "severity": "error",
            })
        return base

    # ── Approval ──────────────────────────────────────────────

    def get_approval_checklist(self) -> List[Dict[str, Any]]:
        checks = []
        for c in APPROVAL_CHECKLIST_DEMO:
            check = dict(c)
            if check["id"] == "mapping_complete":
                check["status"] = len(self._canonical.mappings) > 0
            elif check["id"] == "validation_passed":
                all_pass = all(
                    chk["status"] in ("pass", "info")
                    for chk in self.get_validation_checks()
                )
                check["status"] = all_pass
            elif check["id"] == "required_fields":
                check["status"] = len(self._canonical.get_required_missing()) == 0
            elif check["id"] == "business_schema":
                check["status"] = len(self._canonical.mappings) >= 6
            elif check["id"] == "dataset_generated":
                check["status"] = True  # canonical dataset is always generated after Sprint 4A
            checks.append(check)
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
