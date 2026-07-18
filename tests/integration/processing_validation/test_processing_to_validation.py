"""Integration Tests — Processing → Validation."""

import pytest
import polars as pl

from dav_platform.core.contracts import (
    AggregationConfig,
    AggregationResult,
    CanonicalDataset,
    CalculationConfig,
    CalculationResult,
    ProcessingConfig,
    ProcessingResult,
    ProcessingStatistics,
    ValidationConfig,
    ValidationIssue,
    ValidationRule,
    ValidationSeverity,
    AggregationStrategy,
)
from dav_platform.processing.engine import ProcessingEngine
from dav_platform.validation.engine import ValidationEngine


def _make_processing_result():
    df = pl.DataFrame({
        "store_id": ["S1", "S1", "S2", "S2", "S3", "S3"],
        "upc": ["U1", "U2", "U1", "U2", "U1", "U2"],
        "category": ["CatA", "CatA", "CatA", "CatB", "CatB", "CatB"],
        "sales": [100.0, 200.0, 150.0, 250.0, 300.0, 100.0],
        "quantity": [10, 20, 15, 25, 30, 10],
    })
    return ProcessingResult(
        df=df,
        operation="aggregate_and_calculate",
        row_count=df.height,
        column_count=df.width,
    )


def _make_canonical_dataset():
    df = pl.DataFrame({
        "store_id": ["S1", "S1", "S2", "S2", "S3", "S3"],
        "upc": ["U1", "U2", "U1", "U2", "U1", "U2"],
        "category": ["CatA", "CatA", "CatA", "CatB", "CatB", "CatB"],
        "sales": [100.0, 200.0, 150.0, 250.0, 300.0, 100.0],
        "quantity": [10, 20, 15, 25, 30, 10],
    })
    return CanonicalDataset(
        dataframe=df,
        canonical_columns=list(df.columns),
    )


class TestProcessingToValidationIntegration:
    def test_process_then_validate_no_rules(self):
        pr = _make_processing_result()
        engine = ValidationEngine()
        result = engine.validate(pr)
        assert result.passed is True
        assert result.total_rows_checked == 6

    def test_process_then_validate_store_totals(self):
        pr = _make_processing_result()
        engine = ValidationEngine()
        result = engine.validate_store_totals(
            pr.df,
            {"sales": 1100.0, "quantity": 110},
            tolerance=0.01,
        )
        assert result.passed is True

    def test_process_then_validate_store_totals_fail(self):
        pr = _make_processing_result()
        engine = ValidationEngine()
        result = engine.validate_store_totals(
            pr.df,
            {"sales": 2000.0},
            tolerance=0.01,
        )
        assert result.passed is False

    def test_full_pipeline_with_aggregation(self):
        proc_engine = ProcessingEngine()
        agg_config = ProcessingConfig(
            group_columns=["store_id"],
            aggregation_configs=[
                AggregationConfig(column="sales", strategy=AggregationStrategy.SUM),
                AggregationConfig(column="quantity", strategy=AggregationStrategy.SUM),
            ],
        )
        agg_result = proc_engine.aggregate(_make_canonical_dataset(), agg_config)

        val_engine = ValidationEngine()
        result = val_engine.validate(
            _make_processing_result(),
            aggregation_results=[agg_result],
        )
        assert result.passed is True

    def test_full_pipeline_with_calculation(self):
        proc_engine = ProcessingEngine()
        calc_config = ProcessingConfig(
            calculation_configs=[
                CalculationConfig(name="price", columns=["sales", "quantity"], operation="ratio", alias="unit_price"),
            ],
        )
        calc_result = proc_engine.calculate(_make_canonical_dataset(), calc_config)

        val_engine = ValidationEngine()
        result = val_engine.validate(
            _make_processing_result(),
            calculation_results=[calc_result],
        )
        assert result.passed is True

    def test_item_level_validation(self):
        pr = _make_processing_result()
        engine = ValidationEngine()
        expected = {
            "S1": {"sales": 300.0},
            "S2": {"sales": 400.0},
            "S3": {"sales": 400.0},
        }
        result = engine.validate_item_totals(pr.df, "store_id", expected, tolerance=0.01)
        assert result.passed is True

    def test_item_level_validation_fail(self):
        pr = _make_processing_result()
        engine = ValidationEngine()
        expected = {
            "S1": {"sales": 1000.0},
        }
        result = engine.validate_item_totals(pr.df, "store_id", expected, tolerance=0.01)
        assert result.passed is False

    def test_aggregate_validation(self):
        agg = AggregationResult(
            data=pl.DataFrame({
                "store_id": ["S1", "S2", "S3"],
                "sales": [300.0, 400.0, 400.0],
            }),
            group_columns=["store_id"],
        )
        engine = ValidationEngine()
        result = engine.validate_aggregate_totals(
            agg,
            {"sales": 1100.0},
            tolerance=0.01,
        )
        assert result.passed is True

    def test_with_required_columns_and_ranges(self):
        config = ValidationConfig(
            required_columns=["store_id", "upc", "sales"],
            check_nulls=True,
            check_ranges=True,
        )
        config.column_ranges["sales"] = {"min": 0, "max": 1000}
        engine = ValidationEngine(config=config)
        result = engine.validate(_make_processing_result())
        assert result.passed is True
        assert result.warning_count == 0

    def test_with_null_required_columns_fails(self):
        rule = ValidationRule(
            name="null_required_fields",
            rule_type="null_required_fields",
            columns=["store_id"],
            severity=ValidationSeverity.ERROR,
            parameters={"columns": ["store_id"]},
        )
        config = ValidationConfig(
            rules=[rule],
            required_columns=[],
            check_nulls=True,
        )
        engine = ValidationEngine(config=config)
        df = pl.DataFrame({
            "store_id": ["S1", None, "S3"],
            "upc": ["U1", "U2", "U3"],
            "sales": [100.0, 200.0, 300.0],
        })
        pr = ProcessingResult(df=df, operation="test", row_count=df.height, column_count=df.width)
        result = engine.validate(pr)
        assert result.passed is False
        assert result.error_count > 0

    def test_report_from_pipeline(self):
        pr = _make_processing_result()
        engine = ValidationEngine()
        result = engine.validate(pr)
        report = engine.build_report(result)
        assert report.passed is True
        assert report.statistics is not None
