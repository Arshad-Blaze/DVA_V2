"""Tests — Validation Layer: Configuration, Statistics, Metadata, Report."""

import pytest

from dav_platform.core.contracts import (
    ValidationConfig,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    ValidationSummary,
    ValidationStatistics,
    ValidationReportData,
)
from dav_platform.validation.configuration import ValidationConfigBuilder, build_validation_config
from dav_platform.validation.statistics import ValidationStatisticsEngine
from dav_platform.validation.metadata import MetadataCollector
from dav_platform.validation.report import ValidationReportBuilder


class TestValidationConfigBuilder:
    def test_build_default(self):
        config = ValidationConfigBuilder().build()
        assert isinstance(config, ValidationConfig)
        assert config.check_completeness is True
        assert config.check_nulls is True

    def test_add_rule(self):
        rule = ValidationRule(name="test_rule", rule_type="test")
        config = ValidationConfigBuilder().add_rule(rule).build()
        assert len(config.rules) == 1
        assert config.rules[0].name == "test_rule"

    def test_add_multiple_rules(self):
        rules = [
            ValidationRule(name="r1", rule_type="t1"),
            ValidationRule(name="r2", rule_type="t2"),
        ]
        config = ValidationConfigBuilder().add_rules(rules).build()
        assert len(config.rules) == 2

    def test_chained_builders(self):
        config = (
            ValidationConfigBuilder()
            .check_completeness(False)
            .check_consistency(False)
            .check_uniqueness(True)
            .check_nulls(True)
            .check_ranges(False)
            .max_null_percentage(5.0)
            .required_columns(["a", "b"])
            .column_range("sales", min_val=0, max_val=1000)
            .metadata("key", "value")
            .build()
        )
        assert config.check_completeness is False
        assert config.check_consistency is False
        assert config.check_uniqueness is True
        assert config.max_null_percentage == 5.0
        assert config.required_columns == ["a", "b"]
        assert config.column_ranges["sales"]["min"] == 0
        assert config.column_ranges["sales"]["max"] == 1000
        assert config.metadata["key"] == "value"


class TestBuildValidationConfig:
    def test_convenience_function(self):
        rules = [ValidationRule(name="r1", rule_type="t1")]
        config = build_validation_config(
            rules=rules,
            required_columns=["a", "b"],
            max_null_percentage=3.0,
        )
        assert len(config.rules) == 1
        assert config.required_columns == ["a", "b"]
        assert config.max_null_percentage == 3.0


class TestValidationStatisticsEngine:
    def test_compute_stats(self):
        engine = ValidationStatisticsEngine()
        result = ValidationResult(
            passed=True,
            issues=[],
            total_rows_checked=100,
            error_count=0,
            warning_count=0,
        )
        stats = engine.compute(result, rules_evaluated=5, execution_time=0.5)
        assert stats.total_rules_evaluated == 5
        assert stats.rules_passed == 5
        assert stats.rules_failed == 0
        assert stats.warning_count == 0
        assert stats.execution_time_seconds == 0.5

    def test_compute_with_issues(self):
        engine = ValidationStatisticsEngine()
        issues = [
            ValidationIssue(rule="r1", message="m1", severity=ValidationSeverity.WARNING),
            ValidationIssue(rule="r2", message="m2", severity=ValidationSeverity.ERROR),
            ValidationIssue(rule="r3", message="m3", severity=ValidationSeverity.CRITICAL),
        ]
        result = ValidationResult(
            passed=False,
            issues=issues,
            total_rows_checked=50,
            error_count=2,
            warning_count=1,
        )
        stats = engine.compute(result, rules_evaluated=10, execution_time=1.0)
        assert stats.rules_failed == 3
        assert stats.warning_count == 1
        assert stats.error_count == 1
        assert stats.critical_count == 1
        assert stats.total_entities_checked == 50


class TestMetadataCollector:
    def test_record_rule_evaluated(self):
        mc = MetadataCollector()
        mc.record_rule_evaluated("rule1")
        mc.record_rule_evaluated("rule2")
        meta = mc.get_metadata()
        assert meta["rules_evaluated_count"] == 2

    def test_record_rule_passed(self):
        mc = MetadataCollector()
        mc.record_rule_passed("rule1")
        meta = mc.get_metadata()
        assert meta["rules_passed_count"] == 1

    def test_record_rule_failed(self):
        mc = MetadataCollector()
        issues = [
            ValidationIssue(rule="r1", message="fail", severity=ValidationSeverity.ERROR),
        ]
        mc.record_rule_failed("rule1", issues)
        meta = mc.get_metadata()
        assert meta["rules_failed_count"] == 1
        assert meta["error_count"] == 1

    def test_record_warning(self):
        mc = MetadataCollector()
        issues = [
            ValidationIssue(rule="r1", message="warn", severity=ValidationSeverity.WARNING),
        ]
        mc.record_rule_failed("rule1", issues)
        meta = mc.get_metadata()
        assert meta["warning_count"] == 1

    def test_record_tolerance(self):
        mc = MetadataCollector()
        mc.record_tolerance("r1", 0.05)
        meta = mc.get_metadata()
        assert len(meta["tolerances_used"]) == 1
        assert meta["tolerances_used"][0]["tolerance"] == 0.05

    def test_record_threshold(self):
        mc = MetadataCollector()
        mc.record_threshold("r1", 0.10)
        meta = mc.get_metadata()
        assert len(meta["thresholds_applied"]) == 1

    def test_set_duration(self):
        mc = MetadataCollector()
        mc.set_duration(1.23)
        meta = mc.get_metadata()
        assert meta["execution_duration_seconds"] == 1.23


class TestValidationReportBuilder:
    def test_build_basic(self):
        builder = ValidationReportBuilder()
        result = ValidationResult(passed=True, issues=[], total_rows_checked=10)
        stats = ValidationStatistics(total_rules_evaluated=5, rules_passed=5)
        builder.statistics(stats)
        report = builder.build(result)
        assert report.passed is True
        assert report.total_checks == 5
        assert report.passed_checks == 5
        assert report.failed_checks == 0
        assert report.statistics is stats

    def test_build_with_summaries(self):
        builder = ValidationReportBuilder()
        summary = ValidationSummary(
            entity_type="store", entity_id="S1",
            expected={"sales": 100.0}, actual={"sales": 100.0},
            passed=True,
        )
        builder.add_summary(summary)
        result = ValidationResult(passed=True)
        report = builder.build(result)
        assert len(report.summaries) == 1
        assert report.summaries[0].entity_id == "S1"

    def test_build_with_metadata(self):
        builder = ValidationReportBuilder()
        builder.metadata("source", "test")
        result = ValidationResult(passed=True)
        report = builder.build(result)
        assert report.metadata["source"] == "test"

    def test_build_with_failed_checks(self):
        builder = ValidationReportBuilder()
        stats = ValidationStatistics(total_rules_evaluated=10, rules_failed=3)
        builder.statistics(stats)
        result = ValidationResult(passed=False)
        report = builder.build(result)
        assert report.failed_checks == 3
        assert report.passed_checks == 7
