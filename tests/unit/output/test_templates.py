"""Tests — Output Layer: Templates."""

import polars as pl

from dav_platform.core.contracts import (
    ExecutionMetadata,
    ProcessingStatistics,
    ValidationStatistics,
    ValidationSummary,
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
    TEMPLATE_REGISTRY,
    TopStoresByQuantityTemplate,
    TopStoresBySalesTemplate,
    ValidationSummaryTemplate,
    register_template,
)


class TestValidationSummaryTemplate:
    def test_build_with_stats(self):
        stats = ValidationStatistics(
            total_rules_evaluated=10,
            rules_passed=8,
            rules_failed=2,
            warning_count=1,
            error_count=2,
            critical_count=0,
            validation_coverage=100.0,
            execution_time_seconds=0.5,
            total_entities_checked=50,
        )
        tpl = ValidationSummaryTemplate()
        tpl.build({"statistics": stats})
        headers = tpl.get_headers()
        rows = tpl.get_rows()
        assert "Metric" in headers
        assert all(any(str(v) in str(row) for row in rows) for v in [10, 8, 2])

    def test_build_no_stats(self):
        tpl = ValidationSummaryTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestStoreValidationSummaryTemplate:
    def test_build_with_store_summaries(self):
        summaries = [
            ValidationSummary(entity_type="store", entity_id="S1", passed=True,
                              expected={"sales": 100.0}, actual={"sales": 100.0}),
            ValidationSummary(entity_type="store", entity_id="S2", passed=False,
                              expected={"sales": 200.0}, actual={"sales": 150.0}, issues_count=1),
        ]
        tpl = StoreValidationSummaryTemplate()
        tpl.build({"summaries": summaries})
        rows = tpl.get_rows()
        assert len(rows) == 2
        assert rows[0][0] == "S1"
        assert rows[1][0] == "S2"

    def test_build_no_summaries(self):
        tpl = StoreValidationSummaryTemplate()
        tpl.build({"summaries": []})
        assert tpl.get_rows() == []


class TestTopStoresBySalesTemplate:
    def test_build_with_data(self):
        df = pl.DataFrame({"store_id": ["S1", "S2", "S3"], "sales": [300.0, 200.0, 100.0]})
        tpl = TopStoresBySalesTemplate(2)
        tpl.build({"dataframe": df, "store_column": "store_id", "sales_column": "sales"})
        rows = tpl.get_rows()
        assert len(rows) == 2
        assert rows[0][1] == "S1"
        assert rows[1][1] == "S2"

    def test_build_empty(self):
        tpl = TopStoresBySalesTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestTopStoresByQuantityTemplate:
    def test_build_with_data(self):
        df = pl.DataFrame({"store_id": ["S1", "S2", "S3"], "quantity": [30, 20, 10]})
        tpl = TopStoresByQuantityTemplate(2)
        tpl.build({"dataframe": df, "store_column": "store_id", "quantity_column": "quantity"})
        rows = tpl.get_rows()
        assert len(rows) == 2
        assert rows[0][1] == "S1"

    def test_build_empty(self):
        tpl = TopStoresByQuantityTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestBottomStoresTemplate:
    def test_build_with_data(self):
        df = pl.DataFrame({"store_id": ["S1", "S2", "S3"], "sales": [300.0, 200.0, 100.0]})
        tpl = BottomStoresTemplate(2)
        tpl.build({"dataframe": df, "store_column": "store_id", "sales_column": "sales"})
        rows = tpl.get_rows()
        assert len(rows) == 2
        assert rows[0][1] == "S3"
        assert rows[1][1] == "S2"

    def test_build_empty(self):
        tpl = BottomStoresTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestCategorySummaryTemplate:
    def test_build_with_category_data(self):
        cat_data = [
            {"category": "CatA", "value": 500.0},
            {"category": "CatB", "value": 300.0},
        ]
        tpl = CategorySummaryTemplate()
        tpl.build({"category_data": cat_data})
        rows = tpl.get_rows()
        assert len(rows) == 2
        assert rows[0][0] == "CatA"
        assert "62.5" in rows[0][2]

    def test_build_empty(self):
        tpl = CategorySummaryTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestBusinessStatisticsTemplate:
    def test_build_with_stats(self):
        stats = ProcessingStatistics(
            total_rows=100, unique_stores=5, unique_upcs=20,
            unique_categories=3, unique_brands=10, duplicate_count=0,
        )
        tpl = BusinessStatisticsTemplate()
        tpl.build({"processing_statistics": stats})
        rows = tpl.get_rows()
        assert len(rows) >= 5
        assert any("100" in str(r) for r in rows)
        assert any("5" in str(r) for r in rows)

    def test_build_empty(self):
        tpl = BusinessStatisticsTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestExecutionSummaryTemplate:
    def test_build_with_metadata(self):
        metadata = ExecutionMetadata(
            workflow="aggregate_and_calculate",
            total_steps=3, completed_steps=3,
            failed_steps=0, skipped_steps=0,
            execution_duration=1.5, outcome="success",
        )
        tpl = ExecutionSummaryTemplate()
        tpl.build({"execution_metadata": metadata})
        rows = tpl.get_rows()
        assert len(rows) == 7
        assert any("success" in str(r) for r in rows)

    def test_build_empty(self):
        tpl = ExecutionSummaryTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestMetadataTemplate:
    def test_build_with_data(self):
        data = {"version": "2.0", "source": "test"}
        tpl = MetadataTemplate()
        tpl.build({"metadata": data})
        rows = tpl.get_rows()
        assert len(rows) == 2
        assert ["version", "2.0"] in rows
        assert ["source", "test"] in rows

    def test_build_empty(self):
        tpl = MetadataTemplate()
        tpl.build({"metadata": {}})
        assert tpl.get_rows() == []


class TestDashboardSummaryTemplate:
    def test_build_with_stats(self):
        stats = ValidationStatistics(
            total_rules_evaluated=10, rules_passed=8, rules_failed=2,
        )
        tpl = DashboardSummaryTemplate()
        tpl.build({"statistics": stats})
        rows = tpl.get_rows()
        assert any("Failed" in str(r) for r in rows)

    def test_build_empty(self):
        tpl = DashboardSummaryTemplate()
        tpl.build({})
        assert tpl.get_rows() == []


class TestTemplateRegistry:
    def test_registry_has_builtin_templates(self):
        assert "validation_summary" in TEMPLATE_REGISTRY
        assert "store_validation" in TEMPLATE_REGISTRY
        assert "top_stores_sales" in TEMPLATE_REGISTRY
        assert "top_stores_quantity" in TEMPLATE_REGISTRY
        assert "bottom_stores" in TEMPLATE_REGISTRY
        assert "category_summary" in TEMPLATE_REGISTRY
        assert "business_statistics" in TEMPLATE_REGISTRY
        assert "execution_summary" in TEMPLATE_REGISTRY
        assert "metadata" in TEMPLATE_REGISTRY
        assert "dashboard" in TEMPLATE_REGISTRY

    def test_register_custom_template(self):
        @register_template("custom_test", type)
        class CustomTemplate(ReportTemplate):
            def __init__(self):
                super().__init__("Custom")

            def build(self, context):
                return self

        assert "custom_test" in TEMPLATE_REGISTRY


class TestReportTemplateBase:
    def test_to_dataframe(self):
        tpl = type("T", (ReportTemplate,), {
            "build": lambda self, ctx: self,
        })("Test")
        tpl._headers = ["A", "B"]
        tpl._rows = [[1, 2], [3, 4]]
        df = tpl.to_dataframe()
        assert df.height == 2
        assert df.width == 2
