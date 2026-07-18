"""Tests — Output Layer: Excel, Engine."""

import pytest
import polars as pl
import tempfile
import os
import json

from dav_platform.core.contracts import (
    OutputConfig,
    ValidationStatistics,
    ValidationReportData,
)
from dav_platform.output.excel import ExcelExporter
from dav_platform.output.engine import OutputEngine


# ---------------------------------------------------------------------------
# Test ExcelExporter
# ---------------------------------------------------------------------------
class TestExcelExporter:
    def test_export_creates_workbook(self):
        exporter = ExcelExporter()
        reports = [
            {"title": "Test Sheet", "headers": ["A", "B"], "rows": [[1, 2], [3, 4]]},
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            result = exporter.export(reports, path)
            assert os.path.exists(result)
            assert result.endswith(".xlsx")
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_export_multiple_sheets(self):
        exporter = ExcelExporter()
        reports = [
            {"title": "Sheet1", "headers": ["X"], "rows": [["a"]]},
            {"title": "Sheet2", "headers": ["Y"], "rows": [["b"]]},
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            result = exporter.export(reports, path)
            assert os.path.exists(result)
        finally:
            os.unlink(path)

    def test_export_empty_report(self):
        exporter = ExcelExporter()
        reports = [
            {"title": "Empty", "headers": [], "rows": []},
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            result = exporter.export(reports, path)
            assert os.path.exists(result)
        finally:
            os.unlink(path)

    def test_export_no_reports(self):
        exporter = ExcelExporter()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            result = exporter.export([], path)
            assert os.path.exists(result)
        finally:
            os.unlink(path)

    def test_verify_openpyxl_available(self):
        from dav_platform.output.excel import HAS_OPENPYXL
        assert HAS_OPENPYXL is True


# ---------------------------------------------------------------------------
# Test OutputEngine
# ---------------------------------------------------------------------------
class TestOutputEngine:
    def _make_validation_data(self):
        stats = ValidationStatistics(
            total_rules_evaluated=5, rules_passed=5,
            execution_time_seconds=0.5,
        )
        return ValidationReportData(
            passed=True, total_checks=5, passed_checks=5,
            statistics=stats,
        )

    def test_generate_basic(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert artifacts.manifest is not None
        assert artifacts.statistics is not None
        assert len(artifacts.excel_files) >= 1
        assert len(artifacts.csv_files) >= 1
        assert len(artifacts.json_files) >= 1

    def test_generate_with_dataframe(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        engine = OutputEngine(config)
        df = pl.DataFrame({
            "store_id": ["S1", "S2", "S3"],
            "sales": [300.0, 200.0, 100.0],
            "quantity": [30, 20, 10],
        })
        artifacts = engine.generate(self._make_validation_data(), dataframe=df)
        assert len(artifacts.excel_files) >= 1

    def test_generate_no_excel(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp(), excel_enabled=False)
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert len(artifacts.excel_files) == 0
        assert len(artifacts.csv_files) >= 1

    def test_generate_no_csv(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp(), csv_enabled=False)
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert len(artifacts.excel_files) >= 1
        assert len(artifacts.csv_files) == 0
        assert len(artifacts.json_files) >= 1

    def test_generate_no_json(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp(), json_enabled=False)
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert len(artifacts.json_files) == 0

    def test_generate_all_disabled(self):
        config = OutputConfig(
            output_dir=tempfile.mkdtemp(),
            excel_enabled=False,
            csv_enabled=False,
            json_enabled=False,
        )
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert len(artifacts.excel_files) == 0
        assert len(artifacts.csv_files) == 0
        assert len(artifacts.json_files) == 0

    def test_generate_json_summary_content(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp(), excel_enabled=False, csv_enabled=False)
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert len(artifacts.json_files) >= 1
        json_path = artifacts.json_files[0]
        with open(json_path) as f:
            data = json.load(f)
        assert data["passed"] is True
        assert data["total_checks"] == 5

    def test_generate_manifest(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert artifacts.manifest.total_files >= 2
        assert artifacts.manifest.export_duration_seconds > 0

    def test_generate_statistics(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert artifacts.statistics.total_files_generated >= 2

    def test_generate_metadata(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        engine = OutputEngine(config)
        artifacts = engine.generate(self._make_validation_data())
        assert "export_duration_seconds" in artifacts.metadata

    def test_generate_with_issues(self):
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        engine = OutputEngine(config)
        from dav_platform.core.contracts import ValidationIssue, ValidationSeverity
        issues = [
            ValidationIssue(rule="r1", message="fail", severity=ValidationSeverity.ERROR),
        ]
        data = self._make_validation_data()
        data.passed = False
        data.failed_checks = 1
        data.issues = issues
        artifacts = engine.generate(data)
        assert artifacts.statistics.total_files_generated >= 2

    def test_cleanup_output_dir(self):
        import shutil
        tmpdir = tempfile.mkdtemp()
        config = OutputConfig(output_dir=tmpdir)
        engine = OutputEngine(config)
        engine.generate(self._make_validation_data())
        files = os.listdir(tmpdir)
        assert len(files) >= 1
        shutil.rmtree(tmpdir, ignore_errors=True)
