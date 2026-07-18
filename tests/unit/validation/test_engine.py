"""Tests — Validation Layer: ValidationEngine."""

import pytest
import polars as pl

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
from dav_platform.validation.engine import ValidationEngine
from dav_platform.validation.exceptions import ConfigurationError, InputError, RuleExecutionError


def _make_processing_result(df=None, errors=None):
    if df is None:
        df = pl.DataFrame({
            "store_id": ["S1", "S2", "S3"],
            "upc": ["U1", "U2", "U3"],
            "sales": [100.0, 200.0, 300.0],
            "quantity": [10, 20, 30],
        })
    return ProcessingResult(
        df=df,
        operation="aggregate_and_calculate",
        row_count=df.height,
        column_count=df.width,
        errors=errors or [],
    )


class TestValidationEngineInit:
    def test_default_config(self):
        engine = ValidationEngine()
        assert engine.config is not None
        assert isinstance(engine.config, ValidationConfig)

    def test_custom_config(self):
        config = ValidationConfig(max_null_percentage=5.0)
        engine = ValidationEngine(config=config)
        assert engine.config.max_null_percentage == 5.0


class TestValidateFull:
    def test_pass_when_no_rules(self):
        engine = ValidationEngine()
        result = result = engine.validate(_make_processing_result())
        assert result.passed is True
        assert len(result.issues) == 0

    def test_fail_on_processing_errors(self):
        engine = ValidationEngine()
        pr = _make_processing_result(errors=["File not found"])
        result = engine.validate(pr)
        assert result.passed is False
        assert any("File not found" in i.message for i in result.issues)

    def test_metadata_populated(self):
        engine = ValidationEngine()
        result = engine.validate(_make_processing_result())
        assert "rules_evaluated_count" in result.metadata

    def test_with_required_columns_rule(self):
        config = ValidationConfig(
            required_columns=["store_id", "upc"],
            check_nulls=True,
        )
        engine = ValidationEngine(config=config)
        df = pl.DataFrame({
            "store_id": ["S1", "S2", None],
            "upc": ["U1", "U2", "U3"],
            "sales": [100.0, 200.0, 300.0],
        })
        result = engine.validate(_make_processing_result(df=df))
        assert result.warning_count > 0

    def test_with_column_range_rule(self):
        config = ValidationConfig(check_ranges=True)
        config.column_ranges["sales"] = {"min": 0, "max": 500}
        engine = ValidationEngine(config=config)
        df = pl.DataFrame({
            "store_id": ["S1", "S2"],
            "upc": ["U1", "U2"],
            "sales": [100.0, 600.0],
        })
        result = engine.validate(_make_processing_result(df=df))
        assert result.warning_count > 0

    def test_with_aggregation_results(self):
        engine = ValidationEngine()
        agg = AggregationResult(
            data=pl.DataFrame({"category": ["A", "B"], "sales": [500.0, 600.0]}),
            group_columns=["category"],
        )
        result = engine.validate(
            _make_processing_result(),
            aggregation_results=[agg],
        )
        assert result.passed is True

    def test_with_calculation_results(self):
        engine = ValidationEngine()
        calc = CalculationResult(
            data=pl.DataFrame({"store_id": ["S1"], "margin": [0.15]}),
        )
        result = engine.validate(
            _make_processing_result(),
            calculation_results=[calc],
        )
        assert result.passed is True


class TestValidateStoreTotals:
    def test_pass_when_totals_match(self):
        engine = ValidationEngine()
        df = pl.DataFrame({"sales": [100.0, 200.0, 300.0]})
        result = engine.validate_store_totals(df, {"sales": 600.0}, tolerance=0.01)
        assert result.passed is True
        assert len(result.issues) == 0

    def test_fail_when_totals_differ(self):
        engine = ValidationEngine()
        df = pl.DataFrame({"sales": [100.0, 200.0, 300.0]})
        result = engine.validate_store_totals(df, {"sales": 1000.0}, tolerance=0.01)
        assert result.passed is False
        assert len(result.issues) == 1
        assert "differs" in result.issues[0].message

    def test_missing_column(self):
        engine = ValidationEngine()
        df = pl.DataFrame({"sales": [100.0]})
        result = engine.validate_store_totals(df, {"quantity": 10}, tolerance=0.01)
        assert result.passed is False
        assert "not found" in result.issues[0].message

    def test_zero_expected_with_nonzero_actual(self):
        engine = ValidationEngine()
        df = pl.DataFrame({"sales": [100.0]})
        result = engine.validate_store_totals(df, {"sales": 0.0}, tolerance=0.01)
        assert result.passed is False


class TestValidateItemTotals:
    def test_pass_when_items_match(self):
        engine = ValidationEngine()
        df = pl.DataFrame({
            "upc": ["U1", "U1", "U2", "U2"],
            "sales": [100.0, 50.0, 200.0, 100.0],
        })
        expected = {"U1": {"sales": 150.0}, "U2": {"sales": 300.0}}
        result = engine.validate_item_totals(df, "upc", expected, tolerance=0.01)
        assert result.passed is True

    def test_fail_when_item_differs(self):
        engine = ValidationEngine()
        df = pl.DataFrame({
            "upc": ["U1", "U1", "U2", "U2"],
            "sales": [100.0, 50.0, 200.0, 100.0],
        })
        expected = {"U1": {"sales": 150.0}, "U2": {"sales": 500.0}}
        result = engine.validate_item_totals(df, "upc", expected, tolerance=0.01)
        assert result.passed is False
        assert len(result.issues) >= 1

    def test_missing_entity_in_data(self):
        engine = ValidationEngine()
        df = pl.DataFrame({
            "upc": ["U1"],
            "sales": [100.0],
        })
        expected = {"U99": {"sales": 100.0}}
        result = engine.validate_item_totals(df, "upc", expected, tolerance=0.01)
        assert result.passed is False
        assert "not found" in result.issues[0].message

    def test_missing_group_column(self):
        engine = ValidationEngine()
        df = pl.DataFrame({"sales": [100.0]})
        result = engine.validate_item_totals(df, "nonexistent", {}, tolerance=0.01)
        assert result.passed is False


class TestValidateAggregateTotals:
    def test_pass_when_match(self):
        engine = ValidationEngine()
        agg = AggregationResult(
            data=pl.DataFrame({"sales": [500.0, 600.0]}),
        )
        result = engine.validate_aggregate_totals(agg, {"sales": 1100.0}, tolerance=0.01)
        assert result.passed is True

    def test_fail_when_differ(self):
        engine = ValidationEngine()
        agg = AggregationResult(
            data=pl.DataFrame({"sales": [500.0, 600.0]}),
        )
        result = engine.validate_aggregate_totals(agg, {"sales": 2000.0}, tolerance=0.01)
        assert result.passed is False

    def test_missing_column(self):
        engine = ValidationEngine()
        agg = AggregationResult(
            data=pl.DataFrame({"sales": [500.0]}),
        )
        result = engine.validate_aggregate_totals(agg, {"quantity": 100}, tolerance=0.01)
        assert result.passed is False


class TestBuildReport:
    def test_build_report(self):
        engine = ValidationEngine()
        result = engine.validate(_make_processing_result())
        report = engine.build_report(result)
        assert report.passed is True
        assert report.statistics is not None
