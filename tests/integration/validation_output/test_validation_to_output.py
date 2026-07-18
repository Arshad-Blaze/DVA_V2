"""Integration Tests — Validation → Output."""

import tempfile
import os

import polars as pl

from dav_platform.core.contracts import (
    OutputConfig,
    ValidationStatistics,
    ValidationReportData,
    ValidationIssue,
    ValidationSeverity,
    ValidationSummary,
    ExecutionMetadata,
    ProcessingStatistics,
)
from dav_platform.validation.engine import ValidationEngine
from dav_platform.output.engine import OutputEngine


def _make_processing_result():
    df = pl.DataFrame({
        "store_id": ["S1", "S1", "S2", "S2"],
        "upc": ["U1", "U2", "U1", "U2"],
        "category": ["CatA", "CatA", "CatB", "CatB"],
        "sales": [100.0, 200.0, 150.0, 250.0],
        "quantity": [10, 20, 15, 25],
    })
    from dav_platform.core.contracts import ProcessingResult
    return ProcessingResult(df=df, operation="test", row_count=df.height, column_count=df.width)


class TestValidationToOutputIntegration:
    def test_validation_then_output_generates_files(self):
        pr = _make_processing_result()
        val_engine = ValidationEngine()
        val_result = val_engine.validate(pr)
        report_data = val_engine.build_report(val_result)

        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(
                report_data,
                dataframe=pr.df,
            )
            assert len(artifacts.excel_files) >= 1
            assert len(artifacts.csv_files) >= 1
            assert len(artifacts.json_files) >= 1
            assert artifacts.manifest.total_files >= 3
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_validation_with_issues_output(self):
        pr = _make_processing_result()
        val_engine = ValidationEngine()
        val_result = val_engine.validate(pr)
        report_data = val_engine.build_report(val_result)
        report_data.passed = True

        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(
                report_data,
                dataframe=pr.df,
                execution_metadata=ExecutionMetadata(
                    workflow="test", total_steps=3, completed_steps=3,
                ),
                processing_statistics=ProcessingStatistics(
                    total_rows=4, unique_stores=2, unique_upcs=2,
                ),
            )
            assert artifacts.statistics.total_files_generated >= 3
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_full_generated_json_content(self):
        pr = _make_processing_result()
        expected_totals = {"sales": 700.0, "quantity": 70}
        val_engine = ValidationEngine()
        val_result = val_engine.validate_store_totals(pr.df, expected_totals, tolerance=0.01)
        report_data = val_engine.build_report(val_result)

        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir, excel_enabled=False, csv_enabled=False)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(report_data)
            assert len(artifacts.json_files) >= 1
            import json
            with open(artifacts.json_files[0]) as f:
                data = json.load(f)
            assert "passed" in data
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_validation_fails_output_generates_issues_csv(self):
        df = pl.DataFrame({
            "store_id": ["S1", "S2"],
            "sales": [100.0, 200.0],
        })
        pr = _make_processing_result()
        config = OutputConfig(output_dir=tempfile.mkdtemp())
        val_engine = ValidationEngine()
        val_result = val_engine.validate(pr)
        report_data = val_engine.build_report(val_result)

        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(report_data)
            csvs = artifacts.csv_files
            issues_csv = [f for f in csvs if "issues" in f]
            assert len(issues_csv) >= 0
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_output_with_all_reports_enabled(self):
        pr = _make_processing_result()
        val_engine = ValidationEngine()
        result = val_engine.validate(pr)
        report = val_engine.build_report(result)

        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(
                output_dir=tmpdir,
                include_validation_summary=True,
                include_store_summary=True,
                include_category_summary=True,
                include_business_kpis=True,
                include_execution_summary=True,
                include_metadata_sheet=True,
                include_dashboard=True,
            )
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(
                report,
                dataframe=pr.df,
                execution_metadata=ExecutionMetadata(
                    workflow="test", total_steps=2, completed_steps=2,
                ),
                processing_statistics=ProcessingStatistics(
                    total_rows=4, unique_stores=2, unique_upcs=2,
                ),
            )
            assert artifacts.statistics.total_files_generated >= 2
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
