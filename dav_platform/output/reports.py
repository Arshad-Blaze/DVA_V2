"""Output Layer — Report Builder.

Assembles report templates into structured report data.
"""

from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import (
    ExecutionMetadata,
    OutputConfig,
    ProcessingStatistics,
    ValidationReportData,
    ValidationStatistics,
)
from dav_platform.output.templates import (
    BottomStoresTemplate,
    BusinessStatisticsTemplate,
    CategorySummaryTemplate,
    DashboardSummaryTemplate,
    ExecutionSummaryTemplate,
    MetadataTemplate,
    ReportTemplate,
    StoreValidationSummaryTemplate,
    TopStoresByQuantityTemplate,
    TopStoresBySalesTemplate,
    ValidationSummaryTemplate,
)


class ReportBuilder:
    """Assembles all report templates into report data.

    Each report is a dict with 'title', 'headers', 'rows'.
    """

    def __init__(self, config: OutputConfig):
        self._config = config

    def build_all(
        self,
        validation_data: ValidationReportData,
        df: Optional[pl.DataFrame] = None,
        execution_metadata: Optional[ExecutionMetadata] = None,
        processing_statistics: Optional[ProcessingStatistics] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Build all configured reports."""
        ctx = context or {}
        ctx.update({
            "statistics": validation_data.statistics,
            "summaries": validation_data.summaries,
            "issues": validation_data.issues,
            "dataframe": df,
            "execution_metadata": execution_metadata,
            "processing_statistics": processing_statistics,
            "metadata": validation_data.metadata,
        })

        reports = []

        if self._config.include_validation_summary:
            reports.append(self._build(ValidationSummaryTemplate(), ctx))

        if self._config.include_store_summary and validation_data.summaries:
            reports.append(self._build(StoreValidationSummaryTemplate(), ctx))

        if df is not None and self._config.include_business_kpis:
            top_n = self._config.max_top_stores
            ctx_sales = {**ctx, "n": top_n}
            reports.append(self._build(TopStoresBySalesTemplate(top_n), ctx_sales))
            reports.append(self._build(TopStoresByQuantityTemplate(top_n), ctx_sales))
            reports.append(self._build(BottomStoresTemplate(self._config.max_bottom_stores), ctx_sales))

        if self._config.include_category_summary:
            reports.append(self._build(CategorySummaryTemplate(), ctx))

        if processing_statistics and self._config.include_business_kpis:
            reports.append(self._build(BusinessStatisticsTemplate(), ctx))

        if execution_metadata and self._config.include_execution_summary:
            reports.append(self._build(ExecutionSummaryTemplate(), ctx))

        if self._config.include_metadata_sheet:
            reports.append(self._build(MetadataTemplate(), ctx))

        if self._config.include_dashboard:
            reports.append(self._build(DashboardSummaryTemplate(), ctx))

        return [r for r in reports if r is not None]

    def _build(self, template: ReportTemplate, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            template.build(ctx)
            return {
                "title": template.title,
                "headers": template.get_headers(),
                "rows": template.get_rows(),
            }
        except Exception:
            return None
