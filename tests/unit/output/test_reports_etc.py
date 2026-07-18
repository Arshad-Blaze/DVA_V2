"""Tests — Output Layer: Reports, CsvExport, Manifest, Metadata, Statistics."""

import pytest
import polars as pl
import tempfile
import os

from dav_platform.core.contracts import (
    ExecutionMetadata,
    OutputConfig,
    OutputStatistics,
    ProcessingStatistics,
    ValidationIssue,
    ValidationReportData,
    ValidationSeverity,
    ValidationStatistics,
    ValidationSummary,
)
from dav_platform.output.reports import ReportBuilder
from dav_platform.output.csv_export import CSVExporter
from dav_platform.output.manifest import ManifestBuilder
from dav_platform.output.metadata import OutputMetadataCollector
from dav_platform.output.statistics import OutputStatisticsEngine


# ---------------------------------------------------------------------------
# Test ReportBuilder
# ---------------------------------------------------------------------------
class TestReportBuilder:
    def _make_validation_data(self):
        stats = ValidationStatistics(
            total_rules_evaluated=5, rules_passed=5,
        )
        return ValidationReportData(
            passed=True, total_checks=5, passed_checks=5,
            statistics=stats,
        )

    def test_build_validation_summary(self):
        config = OutputConfig()
        builder = ReportBuilder(config)
        reports = builder.build_all(self._make_validation_data())
        titles = [r["title"] for r in reports if r]
        assert any("Validation Summary" in t for t in titles)

    def test_build_store_summary(self):
        config = OutputConfig()
        builder = ReportBuilder(config)
        summaries = [
            ValidationSummary(entity_type="store", entity_id="S1", passed=True,
                              expected={"sales": 100.0}, actual={"sales": 100.0}),
        ]
        data = self._make_validation_data()
        data.summaries = summaries
        reports = builder.build_all(data)
        titles = [r["title"] for r in reports if r]
        assert any("Store Validation" in t for t in titles)

    def test_build_top_stores_with_dataframe(self):
        config = OutputConfig()
        builder = ReportBuilder(config)
        df = pl.DataFrame({"store_id": ["S1", "S2", "S3"], "sales": [300.0, 200.0, 100.0], "quantity": [30, 20, 10]})
        reports = builder.build_all(self._make_validation_data(), df=df)
        titles = [r["title"] for r in reports if r]
        assert any("Top 5" in t for t in titles)
        assert any("Bottom 5" in t for t in titles)

    def test_build_does_not_include_disabled_reports(self):
        config = OutputConfig(
            include_validation_summary=False,
            include_store_summary=False,
            include_business_kpis=False,
            include_category_summary=False,
            include_execution_summary=False,
            include_metadata_sheet=False,
            include_dashboard=False,
        )
        builder = ReportBuilder(config)
        reports = builder.build_all(self._make_validation_data())
        assert len(reports) == 0

    def test_build_with_execution_metadata(self):
        config = OutputConfig()
        builder = ReportBuilder(config)
        metadata = ExecutionMetadata(workflow="test", total_steps=3, completed_steps=3)
        reports = builder.build_all(self._make_validation_data(), execution_metadata=metadata)
        titles = [r["title"] for r in reports if r]
        assert any("Execution" in t for t in titles)

    def test_build_with_processing_stats(self):
        config = OutputConfig()
        builder = ReportBuilder(config)
        ps = ProcessingStatistics(total_rows=100, unique_stores=5)
        reports = builder.build_all(self._make_validation_data(), processing_statistics=ps)
        titles = [r["title"] for r in reports if r]
        assert any("Business Statistics" in t for t in titles)


# ---------------------------------------------------------------------------
# Test CSVExporter
# ---------------------------------------------------------------------------
class TestCSVExporter:
    def test_export_reports(self):
        exporter = CSVExporter()
        reports = [
            {"title": "Test", "headers": ["A", "B"], "rows": [[1, 2], [3, 4]]},
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            result = exporter.export(reports, path)
            assert os.path.exists(result)
            with open(result) as fh:
                content = fh.read()
            assert "Test" in content
            assert "A,B" in content
            assert "1,2" in content
        finally:
            os.unlink(path)

    def test_export_multiple_reports(self):
        exporter = CSVExporter()
        reports = [
            {"title": "R1", "headers": ["X"], "rows": [["a"]]},
            {"title": "R2", "headers": ["Y"], "rows": [["b"]]},
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            result = exporter.export(reports, path)
            with open(result) as fh:
                content = fh.read()
            assert "R1" in content
            assert "R2" in content
        finally:
            os.unlink(path)

    def test_export_empty_reports(self):
        exporter = CSVExporter()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            result = exporter.export([], path)
            assert os.path.exists(result)
        finally:
            os.unlink(path)

    def test_export_validation_results(self):
        exporter = CSVExporter()
        issues = [
            ValidationIssue(rule="r1", message="m1", severity=ValidationSeverity.ERROR, column="col1"),
            ValidationIssue(rule="r2", message="m2", severity=ValidationSeverity.WARNING),
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            result = exporter.export_validation_results(issues, path)
            with open(result) as fh:
                content = fh.read()
            assert "r1" in content
            assert "m2" in content
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Test ManifestBuilder
# ---------------------------------------------------------------------------
class TestManifestBuilder:
    def test_build_empty_manifest(self):
        builder = ManifestBuilder()
        manifest = builder.build()
        assert manifest.total_files == 0
        assert manifest.total_size_bytes == 0

    def test_add_file(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(b"test")
            path = f.name
        try:
            builder = ManifestBuilder()
            builder.add_file(path, "excel", rows=10, sheets=2)
            manifest = builder.build()
            assert manifest.total_files == 1
            assert manifest.total_size_bytes == 4
        finally:
            os.unlink(path)

    def test_multiple_files(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"a,b")
            csv_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b"{}")
            json_path = f.name
        try:
            builder = ManifestBuilder()
            builder.add_file(csv_path, "csv").add_file(json_path, "json")
            manifest = builder.build()
            assert manifest.total_files == 2
        finally:
            os.unlink(csv_path)
            os.unlink(json_path)

    def test_duration(self):
        builder = ManifestBuilder()
        builder.start()
        import time
        time.sleep(0.01)
        manifest = builder.build()
        assert manifest.export_duration_seconds > 0


# ---------------------------------------------------------------------------
# Test OutputMetadataCollector
# ---------------------------------------------------------------------------
class TestOutputMetadataCollector:
    def test_defaults(self):
        mc = OutputMetadataCollector()
        meta = mc.get_metadata()
        assert meta["rows_exported"] == 0
        assert meta["sheets_created"] == 0
        assert meta["files_generated"] == []
        assert meta["warnings"] == []
        assert meta["version"] == "2.0"

    def test_set_duration(self):
        mc = OutputMetadataCollector()
        mc.set_duration(1.5)
        assert mc.get_metadata()["export_duration_seconds"] == 1.5

    def test_add_rows(self):
        mc = OutputMetadataCollector()
        mc.add_rows(100)
        mc.add_rows(50)
        assert mc.get_metadata()["rows_exported"] == 150

    def test_add_sheets(self):
        mc = OutputMetadataCollector()
        mc.add_sheets(5)
        assert mc.get_metadata()["sheets_created"] == 5

    def test_add_file(self):
        mc = OutputMetadataCollector()
        mc.add_file("/path/file.xlsx", "excel")
        meta = mc.get_metadata()
        assert len(meta["files_generated"]) == 1
        assert meta["files_generated"][0]["format"] == "excel"

    def test_add_warning(self):
        mc = OutputMetadataCollector()
        mc.add_warning("Something went wrong")
        assert len(mc.get_metadata()["warnings"]) == 1

    def test_add_skipped(self):
        mc = OutputMetadataCollector()
        mc.add_skipped("dashboard", "no data")
        meta = mc.get_metadata()
        assert len(meta["skipped_outputs"]) == 1
        assert meta["skipped_outputs"][0]["name"] == "dashboard"


# ---------------------------------------------------------------------------
# Test OutputStatisticsEngine
# ---------------------------------------------------------------------------
class TestOutputStatisticsEngine:
    def test_compute(self):
        engine = OutputStatisticsEngine()
        stats = engine.compute(
            total_files=3,
            total_sheets=10,
            total_rows=500,
            total_size_bytes=10000,
            generation_time=1.5,
            warnings=[],
        )
        assert stats.total_files_generated == 3
        assert stats.total_sheets_created == 10
        assert stats.total_rows_exported == 500
        assert stats.success_rate == 100.0

    def test_compute_with_warnings(self):
        engine = OutputStatisticsEngine()
        stats = engine.compute(
            total_files=1, total_sheets=0, total_rows=0,
            total_size_bytes=0, generation_time=0.1,
            warnings=["Excel export failed"],
        )
        assert stats.success_rate == 50.0
        assert len(stats.warnings) == 1
