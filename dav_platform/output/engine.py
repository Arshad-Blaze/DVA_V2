"""Output Layer — Engine.

Orchestrates report generation and export.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import (
    ExecutionMetadata,
    OutputArtifacts,
    OutputConfig,
    OutputStatistics,
    ProcessingStatistics,
    ValidationReportData,
)
from dav_platform.output.csv_export import CSVExporter
from dav_platform.output.excel import ExcelExporter
from dav_platform.output.manifest import ManifestBuilder
from dav_platform.output.metadata import OutputMetadataCollector
from dav_platform.output.reports import ReportBuilder
from dav_platform.output.statistics import OutputStatisticsEngine
from dav_platform.output.exceptions import ExportError, MissingInputError


class OutputEngine:
    """Presentation and export engine.

    Converts validated business results into consumable artifacts.
    Performs NO aggregation, NO calculation, NO validation.
    """

    def __init__(self, config: Optional[OutputConfig] = None):
        self._config = config or OutputConfig()
        self._report_builder = ReportBuilder(self._config)
        self._excel_exporter = ExcelExporter()
        self._csv_exporter = CSVExporter()
        self._manifest_builder = ManifestBuilder()
        self._metadata_collector = OutputMetadataCollector()
        self._statistics_engine = OutputStatisticsEngine()

    @property
    def config(self) -> OutputConfig:
        return self._config

    def generate(
        self,
        validation_data: ValidationReportData,
        dataframe: Optional[pl.DataFrame] = None,
        execution_metadata: Optional[ExecutionMetadata] = None,
        processing_statistics: Optional[ProcessingStatistics] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> OutputArtifacts:
        """Generate all output artifacts.

        Args:
            validation_data: Structured validation results.
            dataframe: Optional DataFrame for top/bottom store rankings.
            execution_metadata: Optional execution metadata.
            processing_statistics: Optional processing statistics.
            context: Optional additional context for templates.

        Returns:
            OutputArtifacts with file paths, manifest, and statistics.
        """
        start = time.time()
        base_dir = self._config.output_dir
        os.makedirs(base_dir, exist_ok=True)

        self._manifest_builder.start()

        reports = self._report_builder.build_all(
            validation_data=validation_data,
            df=dataframe,
            execution_metadata=execution_metadata,
            processing_statistics=processing_statistics,
            context=context,
        )

        all_files = []
        total_sheets = 0
        total_rows = 0
        warnings = []

        if self._config.excel_enabled and reports:
            try:
                excel_path = os.path.join(base_dir, "dva_validation_report.xlsx")
                actual_path = self._excel_exporter.export(reports, excel_path)
                all_files.append(actual_path)
                sheet_count = len(reports)
                total_sheets += sheet_count
                total_rows += sum(len(r.get("rows", [])) for r in reports)
                self._manifest_builder.add_file(
                    actual_path, "excel",
                    rows=total_rows, sheets=sheet_count,
                )
                self._metadata_collector.add_file(actual_path, "excel")
                self._metadata_collector.add_sheets(sheet_count)
                self._metadata_collector.add_rows(total_rows)
            except Exception as e:
                warnings.append(f"Excel export failed: {e}")

        if self._config.csv_enabled and reports:
            try:
                csv_path = os.path.join(base_dir, "dva_validation_report.csv")
                actual_path = self._csv_exporter.export(reports, csv_path)
                all_files.append(actual_path)
                self._manifest_builder.add_file(actual_path, "csv")
                self._metadata_collector.add_file(actual_path, "csv")
            except Exception as e:
                warnings.append(f"CSV export failed: {e}")

        if self._config.csv_enabled and validation_data.issues:
            try:
                issues_path = os.path.join(base_dir, "dva_validation_issues.csv")
                actual_path = self._csv_exporter.export_validation_results(
                    validation_data.issues, issues_path
                )
                all_files.append(actual_path)
                self._manifest_builder.add_file(actual_path, "csv")
                self._metadata_collector.add_file(actual_path, "csv")
            except Exception as e:
                warnings.append(f"CSV issues export failed: {e}")

        if self._config.json_enabled:
            try:
                json_path = os.path.join(base_dir, "dva_summary.json")
                json_data = {
                    "passed": validation_data.passed,
                    "total_checks": validation_data.total_checks,
                    "passed_checks": validation_data.passed_checks,
                    "failed_checks": validation_data.failed_checks,
                    "statistics": {
                        "rules_evaluated": validation_data.statistics.total_rules_evaluated,
                        "rules_passed": validation_data.statistics.rules_passed,
                        "rules_failed": validation_data.statistics.rules_failed,
                        "warning_count": validation_data.statistics.warning_count,
                        "error_count": validation_data.statistics.error_count,
                        "critical_count": validation_data.statistics.critical_count,
                    } if validation_data.statistics else {},
                    "warnings": warnings,
                }
                if validation_data.metadata:
                    json_data["metadata"] = validation_data.metadata

                with open(json_path, "w") as f:
                    json.dump(json_data, f, indent=2)

                all_files.append(json_path)
                self._manifest_builder.add_file(json_path, "json")
                self._metadata_collector.add_file(json_path, "json")
            except Exception as e:
                warnings.append(f"JSON export failed: {e}")

        for w in warnings:
            self._metadata_collector.add_warning(w)

        manifest = self._manifest_builder.build()
        duration = time.time() - start
        self._metadata_collector.set_duration(duration)

        excel_files = [f for f in all_files if f.endswith(".xlsx")]
        csv_files = [f for f in all_files if f.endswith(".csv")]
        json_files = [f for f in all_files if f.endswith(".json")]

        stats = self._statistics_engine.compute(
            total_files=len(all_files),
            total_sheets=total_sheets,
            total_rows=total_rows,
            total_size_bytes=manifest.total_size_bytes,
            generation_time=duration,
            warnings=warnings,
        )

        return OutputArtifacts(
            excel_files=excel_files,
            csv_files=csv_files,
            json_files=json_files,
            manifest=manifest,
            statistics=stats,
            metadata=self._metadata_collector.get_metadata(),
        )
