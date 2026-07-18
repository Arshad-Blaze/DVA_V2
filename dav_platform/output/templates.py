"""Output Layer — Report Templates.

Template Pattern for reusable report formatting.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import polars as pl


class ReportTemplate(ABC):
    """Base class for all report templates."""

    def __init__(self, title: str):
        self.title = title
        self._data: Optional[pl.DataFrame] = None
        self._headers: List[str] = []
        self._rows: List[List[Any]] = []

    @abstractmethod
    def build(self, context: Dict[str, Any]) -> "ReportTemplate":
        """Build the report data from context."""
        ...

    def get_headers(self) -> List[str]:
        return self._headers

    def get_rows(self) -> List[List[Any]]:
        return self._rows

    def to_dataframe(self) -> pl.DataFrame:
        return pl.DataFrame(self._rows, schema=self._headers, orient="row")


class ValidationSummaryTemplate(ReportTemplate):
    """Template for validation summary report."""

    def __init__(self):
        super().__init__("Validation Summary")

    def build(self, context: Dict[str, Any]) -> "ValidationSummaryTemplate":
        stats = context.get("statistics")
        if stats:
            self._headers = ["Metric", "Value"]
            self._rows = [
                ["Total Rules Evaluated", str(stats.total_rules_evaluated)],
                ["Rules Passed", str(stats.rules_passed)],
                ["Rules Failed", str(stats.rules_failed)],
                ["Warnings", str(stats.warning_count)],
                ["Errors", str(stats.error_count)],
                ["Critical", str(stats.critical_count)],
                ["Entities Checked", str(stats.total_entities_checked)],
                ["Execution Time (s)", f"{stats.execution_time_seconds:.3f}"],
                ["Coverage", f"{stats.validation_coverage:.1f}%"],
            ]
        return self


class StoreValidationSummaryTemplate(ReportTemplate):
    """Template for store-level validation results."""

    def __init__(self):
        super().__init__("Store Validation Summary")

    def build(self, context: Dict[str, Any]) -> "StoreValidationSummaryTemplate":
        summaries = context.get("summaries", [])
        store_summaries = [s for s in summaries if s.entity_type == "store"]
        if store_summaries:
            self._headers = ["Store", "Passed", "Issues", "Expected Sales", "Actual Sales"]
            self._rows = [
                [s.entity_id, str(s.passed), str(s.issues_count),
                 str(s.expected.get("sales", "")), str(s.actual.get("sales", ""))]
                for s in store_summaries
            ]
        return self


class TopStoresBySalesTemplate(ReportTemplate):
    """Template for top N stores by sales."""

    def __init__(self, n: int = 5):
        super().__init__(f"Top {n} Stores by Sales")
        self._n = n

    def build(self, context: Dict[str, Any]) -> "TopStoresBySalesTemplate":
        df = context.get("dataframe")
        sales_col = context.get("sales_column", "sales")
        store_col = context.get("store_column", "store_id")
        if df is not None and store_col in df.columns and sales_col in df.columns:
            sorted_df = df.sort(sales_col, descending=True).head(self._n)
            self._headers = ["Rank", store_col, sales_col]
            self._rows = [
                [i + 1, row[store_col], row[sales_col]]
                for i, row in enumerate(sorted_df.iter_rows(named=True))
            ]
        return self


class TopStoresByQuantityTemplate(ReportTemplate):
    """Template for top N stores by quantity."""

    def __init__(self, n: int = 5):
        super().__init__(f"Top {n} Stores by Quantity")
        self._n = n

    def build(self, context: Dict[str, Any]) -> "TopStoresByQuantityTemplate":
        df = context.get("dataframe")
        qty_col = context.get("quantity_column", "quantity")
        store_col = context.get("store_column", "store_id")
        if df is not None and store_col in df.columns and qty_col in df.columns:
            sorted_df = df.sort(qty_col, descending=True).head(self._n)
            self._headers = ["Rank", store_col, qty_col]
            self._rows = [
                [i + 1, row[store_col], row[qty_col]]
                for i, row in enumerate(sorted_df.iter_rows(named=True))
            ]
        return self


class BottomStoresTemplate(ReportTemplate):
    """Template for bottom N stores by sales."""

    def __init__(self, n: int = 5):
        super().__init__(f"Bottom {n} Stores by Sales")
        self._n = n

    def build(self, context: Dict[str, Any]) -> "BottomStoresTemplate":
        df = context.get("dataframe")
        sales_col = context.get("sales_column", "sales")
        store_col = context.get("store_column", "store_id")
        if df is not None and store_col in df.columns and sales_col in df.columns:
            sorted_df = df.sort(sales_col, descending=False).head(self._n)
            self._headers = ["Rank", store_col, sales_col]
            self._rows = [
                [i + 1, row[store_col], row[sales_col]]
                for i, row in enumerate(sorted_df.iter_rows(named=True))
            ]
        return self


class CategorySummaryTemplate(ReportTemplate):
    """Template for category-level summary.
    
    Consumes pre-computed category data; NEVER aggregates.
    """

    def __init__(self):
        super().__init__("Category Summary")

    def build(self, context: Dict[str, Any]) -> "CategorySummaryTemplate":
        category_data = context.get("category_data", [])
        if category_data:
            total = sum(row.get("value", 0) for row in category_data)
            self._headers = ["Category", "Value", "% of Total"]
            self._rows = [
                [row["category"], row["value"],
                 f"{(row['value'] / total * 100):.1f}%" if total > 0 else "0%"]
                for row in category_data
            ]
        return self


class BusinessStatisticsTemplate(ReportTemplate):
    """Template for business statistics overview."""

    def __init__(self):
        super().__init__("Business Statistics")

    def build(self, context: Dict[str, Any]) -> "BusinessStatisticsTemplate":
        stats = context.get("processing_statistics")
        if stats:
            self._headers = ["Metric", "Value"]
            self._rows = [
                ["Total Rows", str(stats.total_rows)],
                ["Unique Stores", str(stats.unique_stores)],
                ["Unique UPCs", str(stats.unique_upcs)],
                ["Unique Categories", str(stats.unique_categories)],
                ["Unique Brands", str(stats.unique_brands)],
                ["Duplicate Count", str(stats.duplicate_count)],
            ]
        return self


class ExecutionSummaryTemplate(ReportTemplate):
    """Template for execution summary."""

    def __init__(self):
        super().__init__("Execution Summary")

    def build(self, context: Dict[str, Any]) -> "ExecutionSummaryTemplate":
        metadata = context.get("execution_metadata")
        if metadata:
            self._headers = ["Metric", "Value"]
            self._rows = [
                ["Workflow", metadata.workflow],
                ["Total Steps", str(metadata.total_steps)],
                ["Completed Steps", str(metadata.completed_steps)],
                ["Failed Steps", str(metadata.failed_steps)],
                ["Skipped Steps", str(metadata.skipped_steps)],
                ["Duration (s)", f"{metadata.execution_duration:.3f}"],
                ["Outcome", metadata.outcome],
            ]
        return self


class MetadataTemplate(ReportTemplate):
    """Template for output metadata."""

    def __init__(self):
        super().__init__("Metadata")

    def build(self, context: Dict[str, Any]) -> "MetadataTemplate":
        data = context.get("metadata", {})
        self._headers = ["Key", "Value"]
        self._rows = [[k, str(v)] for k, v in data.items()]
        return self


class DashboardSummaryTemplate(ReportTemplate):
    """Template for executive dashboard summary."""

    def __init__(self):
        super().__init__("Dashboard Summary")

    def build(self, context: Dict[str, Any]) -> "DashboardSummaryTemplate":
        self._headers = ["KPI", "Value"]
        self._rows = []
        stats = context.get("statistics")
        if stats:
            self._rows.append(["Validation Status", "Passed" if stats.rules_failed == 0 else "Failed"])
            self._rows.append(["Rules Failed", str(stats.rules_failed)])
            self._rows.append(["Total Rules", str(stats.total_rules_evaluated)])
        processing_stats = context.get("processing_statistics")
        if processing_stats:
            self._rows.append(["Total Rows Processed", str(processing_stats.total_rows)])
            self._rows.append(["Unique Stores", str(processing_stats.unique_stores)])
            self._rows.append(["Unique UPCs", str(processing_stats.unique_upcs)])
        return self


TEMPLATE_REGISTRY: Dict[str, type] = {}


def register_template(name: str, template_cls: type) -> type:
    TEMPLATE_REGISTRY[name] = template_cls
    return template_cls


register_template("validation_summary", ValidationSummaryTemplate)
register_template("store_validation", StoreValidationSummaryTemplate)
register_template("top_stores_sales", TopStoresBySalesTemplate)
register_template("top_stores_quantity", TopStoresByQuantityTemplate)
register_template("bottom_stores", BottomStoresTemplate)
register_template("category_summary", CategorySummaryTemplate)
register_template("business_statistics", BusinessStatisticsTemplate)
register_template("execution_summary", ExecutionSummaryTemplate)
register_template("metadata", MetadataTemplate)
register_template("dashboard", DashboardSummaryTemplate)
