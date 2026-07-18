"""Reports service — Reports & Insights Center (Sprint 8).

Executive dashboard, business KPIs, validation KPIs, report explorer,
interactive reports, charts, drill down, export center, and history.

Never generates reports — only visualizes and exports backend results.
"""

import csv
import io
import json
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


# ── Demo Data ─────────────────────────────────────────────────────────────────


EXECUTIVE_DASHBOARD_DEMO = {
    "overall_health": "Good",
    "validation_score": 80.0,
    "business_readiness": "Good",
    "execution_runtime": "4.2s",
    "reports_generated": 5,
    "critical_issues": 0,
    "warnings": 2,
    "streaming": True,
}

BUSINESS_KPIS_DEMO = {
    "stores": {"total": 50, "with_data": 45, "missing": 5, "coverage_pct": 90.0},
    "upcs": {"total": 900, "with_data": 892, "missing": 8, "coverage_pct": 99.1},
    "categories": {"total": 15, "with_data": 12, "missing": 3, "coverage_pct": 80.0},
    "brands": {"total": 70, "with_data": 64, "missing": 6, "coverage_pct": 91.4},
    "departments": {"total": 10, "with_data": 8, "missing": 2, "coverage_pct": 80.0},
    "total_sales": 118423.0,
    "total_quantity": 14275,
    "average_basket": 8.30,
    "date_range": {"from": "2026-01-01", "to": "2026-03-31"},
    "growth_metrics": {"sales_qoq": -2.1, "quantity_qoq": -1.8, "basket_qoq": 0.3},
}

VALIDATION_KPIS_DEMO = {
    "passed_rules": 16,
    "failed_rules": 2,
    "warnings": 2,
    "critical": 0,
    "total_rules": 20,
    "store_success_pct": 90.0,
    "upc_success_pct": 99.1,
    "coverage_pct": 85.0,
}

REPORT_EXPLORER_DEMO = {
    "categories": [
        {"id": "summary", "label": "Summary Reports", "icon": "summarize", "count": 4},
        {"id": "store", "label": "Store Reports", "icon": "store", "count": 3},
        {"id": "category", "label": "Category Reports", "icon": "category", "count": 3},
        {"id": "validation", "label": "Validation Reports", "icon": "verified", "count": 3},
    ],
    "types": ["Executive", "Business", "Validation", "Store", "Category", "Brand", "Department", "Custom"],
    "pinned": [
        {"id": "r1", "name": "Executive Summary", "type": "Executive", "generated": "2026-07-19 14:32:05"},
        {"id": "r2", "name": "Validation Report", "type": "Validation", "generated": "2026-07-19 14:32:05"},
    ],
    "recent": [
        {"id": "r1", "name": "Executive Summary", "type": "Executive", "generated": "2026-07-19 14:32:05"},
        {"id": "r2", "name": "Validation Report", "type": "Validation", "generated": "2026-07-19 14:32:05"},
        {"id": "r3", "name": "Store Performance", "type": "Store", "generated": "2026-07-19 14:30:00"},
    ],
}

INTERACTIVE_REPORTS_DEMO = [
    {"id": "r1", "name": "Executive Summary", "type": "Executive", "sections": ["overview", "kpis", "validation"], "downloads": ["csv", "pdf"]},
    {"id": "r2", "name": "Store Summary", "type": "Store", "sections": ["stores", "sales", "quantity"], "downloads": ["csv", "xlsx"]},
    {"id": "r3", "name": "Category Summary", "type": "Category", "sections": ["categories", "sales", "brands"], "downloads": ["csv", "xlsx"]},
    {"id": "r4", "name": "Department Summary", "type": "Department", "sections": ["departments", "sales"], "downloads": ["csv"]},
    {"id": "r5", "name": "Brand Summary", "type": "Brand", "sections": ["brands", "upcs", "sales"], "downloads": ["csv", "pdf"]},
    {"id": "r6", "name": "Top Stores", "type": "Store", "sections": ["top_10", "sales", "growth"], "downloads": ["csv", "xlsx", "pdf"]},
    {"id": "r7", "name": "Bottom Stores", "type": "Store", "sections": ["bottom_10", "issues"], "downloads": ["csv"]},
    {"id": "r8", "name": "Validation Summary", "type": "Validation", "sections": ["rules", "pass_fail", "recommendations"], "downloads": ["csv", "pdf"]},
    {"id": "r9", "name": "Business Statistics", "type": "Executive", "sections": ["kpis", "trends", "comparison"], "downloads": ["csv", "xlsx", "pdf"]},
    {"id": "r10", "name": "Rule Summary", "type": "Validation", "sections": ["all_rules", "severity", "coverage"], "downloads": ["csv"]},
]

CHART_DATA_DEMO = {
    "sales_by_store": {"labels": ["S001", "S002", "S003", "S004", "S005"], "values": [32000, 28000, 25000, 18500, 14923]},
    "sales_by_category": {"labels": ["Dairy", "Bakery", "Beverages", "Snacks", "Produce"], "values": [35000, 28000, 22000, 18500, 14923]},
    "quantity_by_store": {"labels": ["S001", "S002", "S003", "S004", "S005"], "values": [3800, 3400, 3100, 2200, 1775]},
    "validation_distribution": {"labels": ["Passed", "Failed", "Warning", "Critical"], "values": [16, 2, 2, 0]},
    "rule_severity": {"labels": ["Error", "Warning", "Info"], "values": [2, 2, 2]},
    "business_completeness": {"labels": ["Stores", "UPCs", "Categories", "Brands", "Departments"], "values": [90.0, 99.1, 80.0, 91.4, 80.0]},
}

DRILL_DOWN_DEMO = {
    "stores": [
        {"id": "S001", "name": "Store 001", "sales": 32000, "quantity": 3800, "upcs": 180, "validation": "pass"},
        {"id": "S002", "name": "Store 002", "sales": 28000, "quantity": 3400, "upcs": 175, "validation": "pass"},
        {"id": "S003", "name": "Store 003", "sales": 25000, "quantity": 3100, "upcs": 170, "validation": "pass"},
        {"id": "S004", "name": "Store 004", "sales": 18500, "quantity": 2200, "upcs": 165, "validation": "warn"},
        {"id": "S005", "name": "Store 005", "sales": 14923, "quantity": 1775, "upcs": 160, "validation": "fail"},
    ],
    "upcs": [
        {"id": "490123456001", "name": "UPC 001", "sales": 5200, "store": "S001", "validation": "pass"},
        {"id": "490123456002", "name": "UPC 002", "sales": 4800, "store": "S002", "validation": "pass"},
        {"id": "490123456999", "name": "UPC 999", "sales": -299, "store": "S005", "validation": "fail"},
    ],
}

EXPORT_FORMATS = ["csv", "xlsx", "pdf", "json", "zip"]

REPORT_HISTORY_DEMO = [
    {"execution_id": "EXEC-001", "generated": "2026-07-19 14:32:05", "version": "v2.3", "format": "csv/pdf", "status": "completed", "reports": 5},
    {"execution_id": "EXEC-002", "generated": "2026-07-19 14:00:00", "version": "v2.2", "format": "csv", "status": "completed", "reports": 3},
    {"execution_id": "EXEC-003", "generated": "2026-07-18 10:15:00", "version": "v2.1", "format": "xlsx", "status": "completed", "reports": 4},
    {"execution_id": "EXEC-004", "generated": "2026-07-17 08:30:00", "version": "v2.0", "format": "json", "status": "completed", "reports": 2},
]


class ReportsService:
    """Manages Reports & Insights Center state.

    Never generates reports — only visualizes and exports backend results.
    """

    def __init__(self, context=None):
        self._context = context
        self._selected_report: Optional[str] = None
        self._selected_format: str = "csv"
        self._search_query: str = ""
        self._selected_category: Optional[str] = None
        self._selected_chart: Optional[str] = None
        self._drill_down_level: str = "dashboard"
        self._drill_down_id: Optional[str] = None
        self._export_preview_data: Optional[str] = None
        self._on_change: Optional[Callable] = None

    # ── Executive Dashboard ───────────────────────────────────

    @property
    def executive_dashboard(self) -> Dict[str, Any]:
        return dict(EXECUTIVE_DASHBOARD_DEMO)

    # ── Business KPIs ─────────────────────────────────────────

    @property
    def business_kpis(self) -> Dict[str, Any]:
        return dict(BUSINESS_KPIS_DEMO)

    # ── Validation KPIs ───────────────────────────────────────

    @property
    def validation_kpis(self) -> Dict[str, Any]:
        return dict(VALIDATION_KPIS_DEMO)

    # ── Report Explorer ───────────────────────────────────────

    @property
    def report_explorer(self) -> Dict[str, Any]:
        return dict(REPORT_EXPLORER_DEMO)

    @property
    def filtered_reports(self) -> List[Dict[str, Any]]:
        reports = list(INTERACTIVE_REPORTS_DEMO)
        if self._selected_category:
            cat_map = {
                "summary": ["Executive"],
                "store": ["Store"],
                "category": ["Category"],
                "validation": ["Validation"],
            }
            allowed_types = cat_map.get(self._selected_category, [])
            if allowed_types:
                reports = [r for r in reports if r["type"] in allowed_types]
        if self._search_query:
            q = self._search_query.lower()
            reports = [r for r in reports if q in r["name"].lower() or q in r["type"].lower()]
        return reports

    @property
    def report_count(self) -> int:
        return len(INTERACTIVE_REPORTS_DEMO)

    def set_search_query(self, query: str) -> None:
        self._search_query = query
        self._notify()

    def select_category(self, category: Optional[str]) -> None:
        self._selected_category = category
        self._notify()

    def select_report(self, report_id: str) -> None:
        self._selected_report = report_id
        self._notify()

    @property
    def selected_report(self) -> Optional[Dict[str, Any]]:
        for r in INTERACTIVE_REPORTS_DEMO:
            if r["id"] == self._selected_report:
                return dict(r)
        return None

    # ── Interactive Reports ───────────────────────────────────

    @property
    def all_reports(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in INTERACTIVE_REPORTS_DEMO]

    # ── Charts ────────────────────────────────────────────────

    @property
    def chart_data(self) -> Dict[str, Any]:
        return dict(CHART_DATA_DEMO)

    @property
    def chart_keys(self) -> List[str]:
        return list(CHART_DATA_DEMO.keys())

    def select_chart(self, chart_key: Optional[str]) -> None:
        self._selected_chart = chart_key
        self._notify()

    @property
    def selected_chart(self) -> Optional[Dict[str, Any]]:
        if self._selected_chart and self._selected_chart in CHART_DATA_DEMO:
            return dict(CHART_DATA_DEMO[self._selected_chart])
        return None

    # ── Drill Down ────────────────────────────────────────────

    @property
    def drill_down_level(self) -> str:
        return self._drill_down_level

    @property
    def drill_down_id(self) -> Optional[str]:
        return self._drill_down_id

    @property
    def drill_down_data(self) -> Dict[str, Any]:
        return dict(DRILL_DOWN_DEMO)

    def drill_to_store(self, store_id: str) -> None:
        self._drill_down_level = "store"
        self._drill_down_id = store_id
        self._notify()

    def drill_to_upc(self, upc_id: str) -> None:
        self._drill_down_level = "upc"
        self._drill_down_id = upc_id
        self._notify()

    def drill_to_validation(self) -> None:
        self._drill_down_level = "validation"
        self._drill_down_id = None
        self._notify()

    def drill_to_business(self) -> None:
        self._drill_down_level = "business"
        self._drill_down_id = None
        self._notify()

    def drill_up(self) -> None:
        hierarchy = ["dashboard", "store", "upc", "validation", "business"]
        current = self._drill_down_level
        idx = hierarchy.index(current) if current in hierarchy else 0
        self._drill_down_level = hierarchy[max(0, idx - 1)]
        self._drill_down_id = None
        self._notify()

    def drill_reset(self) -> None:
        self._drill_down_level = "dashboard"
        self._drill_down_id = None
        self._notify()

    # ── Export Center ─────────────────────────────────────────

    @property
    def export_formats(self) -> List[str]:
        return list(EXPORT_FORMATS)

    @property
    def selected_format(self) -> str:
        return self._selected_format

    def select_format(self, fmt: str) -> None:
        if fmt in EXPORT_FORMATS:
            self._selected_format = fmt
            self._notify()

    def preview_export(self, report_id: Optional[str] = None) -> str:
        rid = report_id or self._selected_report
        report = next((r for r in INTERACTIVE_REPORTS_DEMO if r["id"] == rid), None)
        if not report:
            return "No report selected for preview."
        fmt = self._selected_format
        buf = io.StringIO()
        if fmt == "csv":
            w = csv.writer(buf)
            w.writerow(["Report", "Type", "Sections", "Format"])
            w.writerow([report["name"], report["type"], "; ".join(report["sections"]), fmt])
        elif fmt == "json":
            buf.write(json.dumps(report, indent=2))
        elif fmt in ("xlsx", "pdf", "zip"):
            buf.write(f"[{fmt.upper()}] Report: {report['name']} ({report['type']})\n")
            buf.write(f"Sections: {', '.join(report['sections'])}\n")
        return buf.getvalue()

    def export_report(self, report_id: Optional[str] = None, fmt: Optional[str] = None) -> str:
        return self.preview_export(report_id or self._selected_report)

    def export_all(self, fmt: Optional[str] = None) -> str:
        fmt = fmt or self._selected_format
        buf = io.StringIO()
        if fmt == "csv":
            w = csv.writer(buf)
            w.writerow(["ID", "Name", "Type", "Sections"])
            for r in INTERACTIVE_REPORTS_DEMO:
                w.writerow([r["id"], r["name"], r["type"], "; ".join(r["sections"])])
        elif fmt == "json":
            buf.write(json.dumps(INTERACTIVE_REPORTS_DEMO, indent=2))
        else:
            buf.write(f"[{fmt.upper()}] All reports exported\n")
        return buf.getvalue()

    # ── Report History ────────────────────────────────────────

    @property
    def report_history(self) -> List[Dict[str, Any]]:
        return [dict(h) for h in REPORT_HISTORY_DEMO]

    # ── Status Bar ────────────────────────────────────────────

    @property
    def status_bar(self) -> Dict[str, Any]:
        selected = self.selected_report
        return {
            "report_count": len(INTERACTIVE_REPORTS_DEMO),
            "current_report": selected["name"] if selected else None,
            "dataset": "Retail Sales Q1 2026",
            "export_status": "Ready" if self._selected_format else "No format selected",
            "filtered_count": len(self.filtered_reports),
        }

    # ── Events ───────────────────────────────────────────────

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
