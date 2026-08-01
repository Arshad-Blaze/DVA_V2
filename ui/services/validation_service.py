"""Validation service — Validation Center (Sprint 7).

Quality control dashboard with heat map, issue explorer,
expected vs actual comparison, rule details, business impact,
suggested actions, and approval workflow.

Never validates data — only visualizes results.
"""

import csv
import io
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

from dav_platform.core.contracts import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
    ValidationStatistics,
    ValidationRule,
    ValidationSummary,
)
from dav_platform.validation.engine import ValidationEngine


DASHBOARD_DEMO = {
    "total_rules": 20,
    "passed": 16,
    "warnings": 2,
    "failed": 2,
    "critical": 0,
    "score": 80.0,
    "business_readiness": "Good",
    "overall_quality": "High",
}

ISSUES_DEMO: List[Dict[str, Any]] = [
    {"rule": "store_sales_not_zero", "severity": "error", "message": "Store S045 has zero total sales", "affected_records": 15, "column": "sales", "entity": "store", "entity_id": "S045", "business_impact": "Store S045 excluded from sales analysis", "recommendation": "Verify source data for Store S045", "category": "Completeness"},
    {"rule": "price_non_negative", "severity": "error", "message": "UPC 490123456999 has negative price (-$2.99)", "affected_records": 3, "column": "price", "entity": "upc", "entity_id": "490123456999", "business_impact": "Negative prices distort margin calculations", "recommendation": "Review pricing data for UPC 490123456999", "category": "Consistency"},
    {"rule": "quantity_mismatch", "severity": "warning", "message": "Quantity mismatch at Store S012 for Dairy category", "affected_records": 47, "column": "quantity", "entity": "store", "entity_id": "S012", "business_impact": "Dairy quantity totals may be inaccurate", "recommendation": "Review Dairy aggregation for Store S012", "category": "Accuracy"},
    {"rule": "mapping_confidence", "severity": "warning", "message": "Low confidence mapping for Promotion column (85%)", "affected_records": 1250, "column": "promotion", "entity": "all", "entity_id": "", "business_impact": "Promotion analysis may include false positives", "recommendation": "Verify Promotion column mapping in Business Mapping Studio", "category": "Data Quality"},
]

HEAT_MAP_ROWS = ["S001", "S002", "S003", "S004", "S005"]
HEAT_MAP_COLUMNS = ["Store", "UPC", "Quantity", "Sales", "Category", "Format", "Date"]
HEAT_MAP_DATA: Dict[str, Dict[str, str]] = {
    "S001": {"Store": "pass", "UPC": "pass", "Quantity": "pass", "Sales": "pass", "Category": "pass", "Format": "pass", "Date": "pass"},
    "S002": {"Store": "pass", "UPC": "pass", "Quantity": "warn", "Sales": "pass", "Category": "pass", "Format": "warn", "Date": "pass"},
    "S003": {"Store": "pass", "UPC": "pass", "Quantity": "pass", "Sales": "pass", "Category": "pass", "Format": "pass", "Date": "pass"},
    "S004": {"Store": "pass", "UPC": "fail", "Quantity": "pass", "Sales": "pass", "Category": "fail", "Format": "pass", "Date": "pass"},
    "S005": {"Store": "fail", "UPC": "pass", "Quantity": "pass", "Sales": "warn", "Category": "pass", "Format": "pass", "Date": "pass"},
}

COMPARISON_DEMO = [
    {"metric": "Store Count", "expected": 50, "actual": 45, "diff": -5, "pct": -10.0},
    {"metric": "UPC Count", "expected": 900, "actual": 892, "diff": -8, "pct": -0.9},
    {"metric": "Total Sales", "expected": 125000, "actual": 118423, "diff": -6577, "pct": -5.3},
    {"metric": "Total Quantity", "expected": 15000, "actual": 14275, "diff": -725, "pct": -4.8},
    {"metric": "Categories", "expected": 15, "actual": 12, "diff": -3, "pct": -20.0},
    {"metric": "Brands", "expected": 70, "actual": 64, "diff": -6, "pct": -8.6},
    {"metric": "Departments", "expected": 10, "actual": 8, "diff": -2, "pct": -20.0},
]

RULES_DEMO: List[Dict[str, Any]] = [
    {"name": "store_sales_not_zero", "description": "Validates that each store has non-zero total sales", "purpose": "Detect stores with missing or zero sales data", "business_meaning": "Zero-sales stores indicate data gaps or ingestion failures", "rule_type": "completeness", "severity": "error", "columns": ["store", "sales"], "affected_rows": 15, "affected_stores": 1, "affected_upcs": 0, "examples": "Store S045 has 0 sales across all items", "resolution": "Verify source file for Store S045, re-upload if necessary"},
    {"name": "price_non_negative", "description": "Validates that all prices are non-negative", "purpose": "Prevent negative prices from distorting calculations", "business_meaning": "Negative prices are invalid in retail context", "rule_type": "consistency", "severity": "error", "columns": ["price"], "affected_rows": 3, "affected_stores": 1, "affected_upcs": 1, "examples": "UPC 490123456999 has price -$2.99", "resolution": "Correct pricing data for affected UPCs"},
    {"name": "quantity_mismatch", "description": "Validates quantity totals against expected ranges", "purpose": "Detect aggregation or data quality issues in quantity", "business_meaning": "Quantity mismatches indicate data integrity issues", "rule_type": "accuracy", "severity": "warning", "columns": ["quantity", "store", "category"], "affected_rows": 47, "affected_stores": 1, "affected_upcs": 12, "examples": "Store S012 Dairy total 147 vs expected 210", "resolution": "Review Dairy product data for Store S012"},
    {"name": "mapping_confidence", "description": "Validates that column mapping confidence meets threshold", "purpose": "Flag low-confidence mappings that may cause incorrect results", "business_meaning": "Low confidence mappings reduce trust in related analyses", "rule_type": "data_quality", "severity": "warning", "columns": ["promotion"], "affected_rows": 1250, "affected_stores": 5, "affected_upcs": 892, "examples": "Promotion column mapped with 85% confidence", "resolution": "Verify Promotion column in Business Mapping Studio"},
    {"name": "store_coverage", "description": "Validates that all expected stores have data", "purpose": "Ensure complete store coverage", "business_meaning": "Missing stores indicate data gaps", "rule_type": "completeness", "severity": "info", "columns": ["store"], "affected_rows": 250, "affected_stores": 5, "affected_upcs": 0, "examples": "5 of 50 expected stores missing from dataset", "resolution": "Upload missing store data files"},
    {"name": "date_format", "description": "Validates date column format consistency", "purpose": "Ensure dates are parseable and consistent", "business_meaning": "Date format issues break time-based analysis", "rule_type": "format", "severity": "info", "columns": ["date"], "affected_rows": 12, "affected_stores": 2, "affected_upcs": 8, "examples": "12 records have non-standard date format", "resolution": "Standardize date format in source file"},
]

BUSINESS_IMPACT_DEMO = {
    "critical": 0,
    "high": 2,
    "medium": 1,
    "low": 1,
    "business_readiness": "Good",
    "affected_stores": 3,
    "affected_sales_pct": 5.3,
    "affected_quantity_pct": 4.8,
    "risk_level": "Low",
}

SUGGESTED_ACTIONS_DEMO = [
    {"action": "Review Mapping", "reason": "Low confidence on Promotion column may cause false positives", "severity": "warning", "navigate": "canonical"},
    {"action": "Review Detection", "reason": "Store S045 missing data may indicate detection issue", "severity": "error", "navigate": "detection"},
    {"action": "Ignore Warnings", "reason": "Quantity mismatch may be acceptable for preliminary analysis", "severity": "info", "navigate": ""},
    {"action": "Continue Anyway", "reason": "Overall quality is High — 80% validation score meets threshold", "severity": "info", "navigate": ""},
]

TIMELINE_STAGES_DEMO = [
    {"id": "execution", "label": "Execution Complete", "icon": "check_circle", "status": "completed"},
    {"id": "store_val", "label": "Store Validation", "icon": "store", "status": "completed"},
    {"id": "upc_val", "label": "UPC Validation", "icon": "barcode", "status": "completed"},
    {"id": "business_rules", "label": "Business Rules", "icon": "rule", "status": "completed"},
    {"id": "summary", "label": "Summary Generated", "icon": "summarize", "status": "completed"},
    {"id": "reports", "label": "Ready for Reports", "icon": "assessment", "status": "current"},
]


class ValidationService:
    """Manages Validation Center state.

    Never validates data — only visualizes backend results.
    """

    def __init__(self, context=None):
        self._context = context
        self._engine = ValidationEngine()
        self._result: Optional[ValidationResult] = None
        self._approved: bool = False
        self._rejected: bool = False
        self._selected_issue: Optional[int] = None
        self._selected_rule: Optional[str] = None
        self._filter_severity: Optional[str] = None
        self._search_query: str = ""
        self._on_change: Optional[Callable] = None

    # ── Result loading from Processing layer ─────────────────

    def load_result(self, result: ValidationResult) -> None:
        """Inject a real ValidationResult from the backend engine."""
        self._result = result
        self._notify()

    def validate(
        self,
        processing_result,
        aggregation_results: Optional[list] = None,
        calculation_results: Optional[list] = None,
        statistics=None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Run the real backend ValidationEngine."""
        result = self._engine.validate(
            processing_result,
            aggregation_results=aggregation_results,
            calculation_results=calculation_results,
            statistics=statistics,
            context=context,
        )
        self._result = result
        self._notify()
        return result

    @property
    def has_result(self) -> bool:
        return self._result is not None

    # ── Dashboard ────────────────────────────────────────────

    @property
    def dashboard(self) -> Dict[str, Any]:
        if self._result is None:
            return dict(DASHBOARD_DEMO)
        return {
            "total_rules": len(self._engine._instantiated_rules) or max(len(self._result.issues), 1),
            "passed": max(0, len(self._result.issues) - self._result.error_count - self._result.warning_count),
            "warnings": self._result.warning_count,
            "failed": self._result.error_count,
            "critical": sum(1 for i in self._result.issues if i.severity == ValidationSeverity.CRITICAL),
            "score": round(self._compute_score(self._result), 1),
            "business_readiness": "Good" if self._result.error_count == 0 else "Needs Review",
            "overall_quality": "High" if self._result.passed else "Low",
        }

    @staticmethod
    def _compute_score(result: ValidationResult) -> float:
        total = len(result.issues)
        if not total:
            return 100.0
        errors = result.error_count * 2 + result.warning_count
        return max(0.0, round(100 - errors * 100 / total, 1))

    # ── Heat Map ─────────────────────────────────────────────

    @property
    def heat_map_rows(self) -> List[str]:
        return list(HEAT_MAP_ROWS)

    @property
    def heat_map_columns(self) -> List[str]:
        return list(HEAT_MAP_COLUMNS)

    @property
    def heat_map_data(self) -> Dict[str, Dict[str, str]]:
        return dict(HEAT_MAP_DATA)

    def get_heat_map_cell(self, row: str, col: str) -> str:
        return HEAT_MAP_DATA.get(row, {}).get(col, "pass")

    # ── Issues ───────────────────────────────────────────────

    @property
    def all_issues(self) -> List[Dict[str, Any]]:
        if self._result is None:
            return [dict(i) for i in ISSUES_DEMO]
        issues = []
        for idx, issue in enumerate(self._result.issues):
            issues.append({
                "rule": issue.rule,
                "severity": issue.severity.value,
                "message": issue.message,
                "affected_records": issue.row_count,
                "column": issue.column or "",
                "entity": "",
                "entity_id": "",
                "business_impact": "",
                "recommendation": "",
                "category": issue.rule,
            })
        return issues

    @property
    def filtered_issues(self) -> List[Dict[str, Any]]:
        issues = self.all_issues
        if self._filter_severity and self._filter_severity != "all":
            issues = [i for i in issues if i["severity"] == self._filter_severity]
        if self._search_query:
            q = self._search_query.lower()
            issues = [i for i in issues if q in i["message"].lower() or q in i["rule"].lower()]
        return issues

    @property
    def issue_count(self) -> int:
        return len(self.filtered_issues)

    def set_severity_filter(self, severity: Optional[str]) -> None:
        self._filter_severity = severity if severity != "all" else None
        self._notify()

    def set_search_query(self, query: str) -> None:
        self._search_query = query
        self._notify()

    def select_issue(self, index: int) -> None:
        self._selected_issue = index
        self._notify()

    @property
    def selected_issue(self) -> Optional[Dict[str, Any]]:
        issues = self.filtered_issues
        if self._selected_issue is not None and self._selected_issue < len(issues):
            return dict(issues[self._selected_issue])
        return None

    # ── Expected vs Actual ───────────────────────────────────

    @property
    def comparison_data(self) -> List[Dict[str, Any]]:
        return [dict(c) for c in COMPARISON_DEMO]

    # ── Rule Details ─────────────────────────────────────────

    @property
    def all_rules(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in RULES_DEMO]

    def select_rule(self, rule_name: str) -> None:
        self._selected_rule = rule_name
        self._notify()

    @property
    def selected_rule(self) -> Optional[Dict[str, Any]]:
        for r in RULES_DEMO:
            if r["name"] == self._selected_rule:
                return dict(r)
        return None

    # ── Business Impact ──────────────────────────────────────

    @property
    def business_impact(self) -> Dict[str, Any]:
        return dict(BUSINESS_IMPACT_DEMO)

    # ── Suggested Actions ────────────────────────────────────

    @property
    def suggested_actions(self) -> List[Dict[str, Any]]:
        return [dict(a) for a in SUGGESTED_ACTIONS_DEMO]

    # ── Timeline ─────────────────────────────────────────────

    @property
    def timeline_stages(self) -> List[Dict[str, Any]]:
        return [dict(t) for t in TIMELINE_STAGES_DEMO]

    # ── Approval ─────────────────────────────────────────────

    @property
    def is_approved(self) -> bool:
        return self._approved

    @property
    def is_rejected(self) -> bool:
        return self._rejected

    def approve(self) -> None:
        self._approved = True
        self._rejected = False
        self._notify()

    def reject(self) -> None:
        self._approved = False
        self._rejected = True
        self._notify()

    def reset(self) -> None:
        self._approved = False
        self._rejected = False
        self._notify()

    # ── Export ───────────────────────────────────────────────

    def export_report(self) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Rule", "Severity", "Message", "Affected Records", "Column", "Business Impact", "Recommendation"])
        for issue in self.all_issues:
            w.writerow([issue["rule"], issue["severity"], issue["message"],
                        issue["affected_records"], issue["column"],
                        issue["business_impact"], issue["recommendation"]])
        return buf.getvalue()

    def export_failed_records(self) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Rule", "Entity", "Entity ID", "Severity", "Affected Records"])
        for issue in self.all_issues:
            if issue["severity"] in ("error", "critical"):
                w.writerow([issue["rule"], issue.get("entity", ""),
                            issue.get("entity_id", ""), issue["severity"],
                            issue["affected_records"]])
        return buf.getvalue()

    # ── Events ───────────────────────────────────────────────

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
