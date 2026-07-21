"""Validation Layer — Engine.

Orchestrates the full validation pipeline.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import polars as pl

logger = logging.getLogger(__name__)

from dav_platform.core.contracts import (
    AggregationResult,
    CalculationResult,
    ProcessingConfig,
    ProcessingResult,
    ProcessingStatistics,
    ValidationConfig,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    ValidationSummary,
)
from dav_platform.validation.configuration import ValidationConfigBuilder
from dav_platform.validation.exceptions import ConfigurationError, InputError, RuleExecutionError
from dav_platform.validation.metadata import MetadataCollector
from dav_platform.validation.report import ValidationReportBuilder
from dav_platform.validation.rules import BaseValidationRule, RuleRegistry, get_registry
from dav_platform.validation.statistics import ValidationStatisticsEngine


class ValidationEngine:
    """Business rule engine for the Validation Layer.

    Orchestrates store-level, item-level, and aggregate validation.
    Consumes ONLY Processing outputs. Never computes or aggregates.
    """

    def __init__(self, config: Optional[ValidationConfig] = None, registry: Optional[RuleRegistry] = None):
        self._config = config or ValidationConfig()
        self._registry = registry or get_registry()
        self._stats_engine = ValidationStatisticsEngine()
        self._metadata_collector = MetadataCollector()
        self._report_builder = ValidationReportBuilder()
        self._instantiated_rules: List[BaseValidationRule] = []

    @property
    def config(self) -> ValidationConfig:
        return self._config

    def validate(
        self,
        processing_result: ProcessingResult,
        aggregation_results: Optional[List[AggregationResult]] = None,
        calculation_results: Optional[List[CalculationResult]] = None,
        statistics: Optional[ProcessingStatistics] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Run the full validation pipeline.

        Args:
            processing_result: Output from the Processing layer.
            aggregation_results: Optional list of aggregation results.
            calculation_results: Optional list of calculation results.
            statistics: Optional processing statistics.
            context: Optional context (expected totals, tolerances, etc.).

        Returns:
            ValidationResult with issues and metadata.
        """
        start = time.time()
        ctx = context or {}

        all_issues: List[ValidationIssue] = []
        total_rows = 0

        if processing_result.errors:
            for err in processing_result.errors:
                all_issues.append(ValidationIssue(
                    rule="processing_errors",
                    message=f"Processing error: {err}",
                    severity=ValidationSeverity.ERROR,
                ))

        df = processing_result.df
        if df.height > 0:
            total_rows = df.height

        config_rules = list(self._config.rules)

        if self._config.required_columns and self._config.check_nulls:
            config_rules.append(ValidationRule(
                name="null_required_fields",
                rule_type="null_required_fields",
                description="Check required columns have no nulls",
                columns=self._config.required_columns,
                severity=ValidationSeverity.WARNING,
                parameters={"columns": self._config.required_columns},
            ))

        for col_name, range_def in self._config.column_ranges.items():
            if self._config.check_ranges:
                config_rules.append(ValidationRule(
                    name=f"value_range_check_{col_name}",
                    rule_type="value_range_check",
                    description=f"Check {col_name} within range",
                    severity=ValidationSeverity.WARNING,
                    parameters={"column": col_name, **range_def},
                ))

        self._instantiated_rules = []
        for rule_def in config_rules:
            if not rule_def.enabled:
                continue
            try:
                rule_instance = self._registry.create(rule_def)
                self._instantiated_rules.append(rule_instance)
            except ValueError:
                continue

        for rule_instance in self._instantiated_rules:
            self._metadata_collector.record_rule_evaluated(rule_instance.name)
            try:
                if df.height > 0:
                    issues = rule_instance.evaluate(df, context=ctx)
                else:
                    issues = []
            except Exception as e:
                raise RuleExecutionError(f"Rule '{rule_instance.name}' failed: {e}") from e

            if issues:
                all_issues.extend(issues)
                self._metadata_collector.record_rule_failed(rule_instance.name, issues)
            else:
                self._metadata_collector.record_rule_passed(rule_instance.name)

        if aggregation_results:
            for agg_result in aggregation_results:
                if agg_result.data.height > 0:
                    for rule_instance in self._instantiated_rules:
                        try:
                            issues = rule_instance.evaluate(agg_result.data, context=ctx)
                            all_issues.extend(issues)
                        except Exception:
                            logger.warning("Rule '%s' failed on aggregation result", rule_instance.name, exc_info=True)

        if calculation_results:
            for calc_result in calculation_results:
                if calc_result.data.height > 0:
                    for rule_instance in self._instantiated_rules:
                        try:
                            issues = rule_instance.evaluate(calc_result.data, context=ctx)
                            all_issues.extend(issues)
                        except Exception:
                            logger.warning("Rule '%s' failed on calculation result", rule_instance.name, exc_info=True)

        execution_time = time.time() - start
        self._metadata_collector.set_duration(execution_time)

        error_count = sum(
            1 for i in all_issues
            if i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
        )
        warning_count = sum(
            1 for i in all_issues if i.severity == ValidationSeverity.WARNING
        )
        passed = error_count == 0

        result = ValidationResult(
            passed=passed,
            issues=all_issues,
            total_rows_checked=total_rows,
            error_count=error_count,
            warning_count=warning_count,
            metadata=self._metadata_collector.get_metadata(),
        )

        stats = self._stats_engine.compute(
            result, len(self._instantiated_rules), execution_time
        )
        self._report_builder.statistics(stats)

        return result

    def validate_store_totals(
        self,
        df: pl.DataFrame,
        expected_totals: Dict[str, float],
        tolerance: float = 0.01,
    ) -> ValidationResult:
        """Validate store-level totals against expected values.

        This is a convenience method for store-level validation.
        It creates a ToleranceCheck rule and evaluates it.
        """
        start = time.time()
        issues: List[ValidationIssue] = []

        for column, expected_val in expected_totals.items():
            if column not in df.columns:
                issues.append(ValidationIssue(
                    rule="store_totals_match",
                    message=f"Column '{column}' not found in data",
                    severity=ValidationSeverity.ERROR, column=column,
                ))
                continue
            actual_val = df[column].sum()
            if expected_val == 0:
                if actual_val != 0:
                    issues.append(ValidationIssue(
                        rule="store_totals_match",
                        message=f"'{column}' expected 0 but got {actual_val}",
                        severity=ValidationSeverity.ERROR, column=column,
                    ))
                continue
            diff_pct = abs(actual_val - expected_val) / abs(expected_val)
            if diff_pct > tolerance:
                issues.append(ValidationIssue(
                    rule="store_totals_match",
                    message=f"'{column}' differs by {diff_pct:.2%} (expected {expected_val}, got {actual_val})",
                    severity=ValidationSeverity.ERROR, column=column,
                ))

        execution_time = time.time() - start
        error_count = len(issues)
        return ValidationResult(
            passed=error_count == 0,
            issues=issues,
            total_rows_checked=df.height,
            error_count=error_count,
            warning_count=0,
            metadata={"tolerance": tolerance, "execution_time_seconds": execution_time},
        )

    def validate_item_totals(
        self,
        df: pl.DataFrame,
        group_column: str,
        expected_totals: Dict[str, Dict[str, float]],
        tolerance: float = 0.01,
    ) -> ValidationResult:
        """Validate item-level (UPC-level) totals against expected values."""
        start = time.time()
        issues: List[ValidationIssue] = []

        if group_column not in df.columns:
            return ValidationResult(
                passed=False,
                issues=[ValidationIssue(
                    rule="item_totals_match",
                    message=f"Group column '{group_column}' not found",
                    severity=ValidationSeverity.ERROR, column=group_column,
                )],
                total_rows_checked=0,
                error_count=1,
            )

        grouped = df.group_by(group_column).agg([
            pl.col(c).sum() for c in df.columns if c != group_column and df[c].dtype in (pl.Float64, pl.Int64, pl.Int32, pl.Float64)
        ])

        for entity_id, totals in expected_totals.items():
            entity_row = grouped.filter(pl.col(group_column) == entity_id)
            if entity_row.height == 0:
                issues.append(ValidationIssue(
                    rule="item_totals_match",
                    message=f"Entity '{entity_id}' not found in '{group_column}'",
                    severity=ValidationSeverity.ERROR, column=group_column,
                ))
                continue
            for col_name, expected_val in totals.items():
                if col_name not in entity_row.columns:
                    continue
                actual_val = entity_row[col_name][0]
                if expected_val == 0:
                    if actual_val != 0:
                        issues.append(ValidationIssue(
                            rule="item_totals_match",
                            message=f"Entity '{entity_id}' column '{col_name}' expected 0, got {actual_val}",
                            severity=ValidationSeverity.ERROR, column=col_name,
                        ))
                    continue
                diff_pct = abs(actual_val - expected_val) / abs(expected_val)
                if diff_pct > tolerance:
                    issues.append(ValidationIssue(
                        rule="item_totals_match",
                        message=f"Entity '{entity_id}' column '{col_name}' differs by {diff_pct:.2%}",
                        severity=ValidationSeverity.ERROR, column=col_name,
                    ))

        execution_time = time.time() - start
        error_count = len(issues)
        return ValidationResult(
            passed=error_count == 0,
            issues=issues,
            total_rows_checked=df.height,
            error_count=error_count,
            warning_count=0,
            metadata={"tolerance": tolerance, "execution_time_seconds": execution_time},
        )

    def validate_aggregate_totals(
        self,
        aggregation_result: AggregationResult,
        expected_totals: Dict[str, float],
        tolerance: float = 0.01,
    ) -> ValidationResult:
        """Validate aggregate outputs (store totals, category totals, etc.)."""
        start = time.time()
        issues: List[ValidationIssue] = []
        df = aggregation_result.data

        for column, expected_val in expected_totals.items():
            if column not in df.columns:
                issues.append(ValidationIssue(
                    rule="aggregate_totals_match",
                    message=f"Column '{column}' not found in aggregation result",
                    severity=ValidationSeverity.ERROR, column=column,
                ))
                continue
            actual_val = df[column].sum()
            if expected_val == 0:
                if actual_val != 0:
                    issues.append(ValidationIssue(
                        rule="aggregate_totals_match",
                        message=f"'{column}' expected 0, got {actual_val}",
                        severity=ValidationSeverity.ERROR, column=column,
                    ))
                continue
            diff_pct = abs(actual_val - expected_val) / abs(expected_val)
            if diff_pct > tolerance:
                issues.append(ValidationIssue(
                    rule="aggregate_totals_match",
                    message=f"'{column}' differs by {diff_pct:.2%} (expected {expected_val}, got {actual_val})",
                    severity=ValidationSeverity.ERROR, column=column,
                ))

        execution_time = time.time() - start
        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            total_rows_checked=df.height,
            error_count=len(issues),
            warning_count=0,
            metadata={"tolerance": tolerance, "execution_time_seconds": execution_time},
        )

    def build_report(self, result: ValidationResult) -> "ValidationReportData":
        """Build a structured report from a ValidationResult."""
        return self._report_builder.build(result)

    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata_collector.get_metadata()
