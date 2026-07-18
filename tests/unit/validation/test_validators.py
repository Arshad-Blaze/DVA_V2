"""Tests — Validation Layer: Built-in Validators."""

import pytest
import polars as pl

from dav_platform.core.contracts import ValidationIssue, ValidationRule, ValidationSeverity
from dav_platform.validation.validators import (
    DifferencePercentageCheck,
    DuplicateDetection,
    MissingEntity,
    NullRequiredFields,
    ToleranceCheck,
    UnexpectedEntity,
    ValueRangeCheck,
)


class TestNullRequiredFields:
    def test_pass_when_no_nulls(self):
        rule = NullRequiredFields(ValidationRule(
            name="null_required_fields",
            rule_type="null_required_fields",
            parameters={"columns": ["store_id"]},
        ))
        df = pl.DataFrame({"store_id": ["S1", "S2", "S3"], "sales": [100, 200, 300]})
        issues = rule.evaluate(df)
        assert len(issues) == 0

    def test_fail_when_nulls_present(self):
        rule = NullRequiredFields(ValidationRule(
            name="null_required_fields",
            rule_type="null_required_fields",
            parameters={"columns": ["store_id"]},
        ))
        df = pl.DataFrame({"store_id": ["S1", None, "S3"], "sales": [100, 200, 300]})
        issues = rule.evaluate(df)
        assert len(issues) == 1
        assert issues[0].column == "store_id"
        assert issues[0].row_count == 1

    def test_empty_dataframe(self):
        rule = NullRequiredFields(ValidationRule(
            name="null_required_fields",
            rule_type="null_required_fields",
            parameters={"columns": ["store_id"]},
        ))
        df = pl.DataFrame({"store_id": pl.Series([], dtype=pl.Utf8)})
        issues = rule.evaluate(df)
        assert len(issues) == 0

    def test_column_not_found(self):
        rule = NullRequiredFields(ValidationRule(
            name="null_required_fields",
            rule_type="null_required_fields",
            parameters={"columns": ["nonexistent"]},
        ))
        df = pl.DataFrame({"store_id": ["S1"]})
        issues = rule.evaluate(df)
        assert len(issues) == 1
        assert "not found" in issues[0].message


class TestDuplicateDetection:
    def test_pass_when_no_duplicates(self):
        rule = DuplicateDetection(ValidationRule(
            name="duplicate_detection",
            rule_type="duplicate_detection",
            parameters={"columns": ["store_id", "upc"]},
        ))
        df = pl.DataFrame({
            "store_id": ["S1", "S2", "S3"],
            "upc": ["U1", "U2", "U3"],
            "sales": [100, 200, 300],
        })
        issues = rule.evaluate(df)
        assert len(issues) == 0

    def test_fail_when_duplicates(self):
        rule = DuplicateDetection(ValidationRule(
            name="duplicate_detection",
            rule_type="duplicate_detection",
            parameters={"columns": ["store_id", "upc"]},
        ))
        df = pl.DataFrame({
            "store_id": ["S1", "S1", "S2"],
            "upc": ["U1", "U1", "U2"],
            "sales": [100, 100, 200],
        })
        issues = rule.evaluate(df)
        assert len(issues) == 1
        assert issues[0].row_count == 1

    def test_empty_dataframe(self):
        rule = DuplicateDetection(ValidationRule(
            name="duplicate_detection",
            rule_type="duplicate_detection",
            parameters={"columns": ["store_id"]},
        ))
        df = pl.DataFrame({"store_id": pl.Series([], dtype=pl.Utf8)})
        issues = rule.evaluate(df)
        assert len(issues) == 0


class TestMissingEntity:
    def test_pass_when_all_present(self):
        rule = MissingEntity(ValidationRule(
            name="missing_entity",
            rule_type="missing_entity",
            parameters={"entity_column": "store_id", "context_key": "expected_stores"},
        ))
        df = pl.DataFrame({"store_id": ["S1", "S2", "S3"]})
        context = {"expected_stores": ["S1", "S2", "S3"]}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 0

    def test_fail_when_missing(self):
        rule = MissingEntity(ValidationRule(
            name="missing_entity",
            rule_type="missing_entity",
            parameters={"entity_column": "store_id", "context_key": "expected_stores"},
        ))
        df = pl.DataFrame({"store_id": ["S1", "S2"]})
        context = {"expected_stores": ["S1", "S2", "S3"]}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 1
        assert "1" in issues[0].message

    def test_no_context_returns_empty(self):
        rule = MissingEntity(ValidationRule(
            name="missing_entity",
            rule_type="missing_entity",
            parameters={"entity_column": "store_id", "context_key": "expected_stores"},
        ))
        df = pl.DataFrame({"store_id": ["S1"]})
        issues = rule.evaluate(df)
        assert len(issues) == 0


class TestUnexpectedEntity:
    def test_pass_when_all_allowed(self):
        rule = UnexpectedEntity(ValidationRule(
            name="unexpected_entity",
            rule_type="unexpected_entity",
            parameters={"entity_column": "store_id", "context_key": "allowed_stores"},
        ))
        df = pl.DataFrame({"store_id": ["S1", "S2"]})
        context = {"allowed_stores": ["S1", "S2", "S3"]}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 0

    def test_fail_when_unexpected(self):
        rule = UnexpectedEntity(ValidationRule(
            name="unexpected_entity",
            rule_type="unexpected_entity",
            parameters={"entity_column": "store_id", "context_key": "allowed_stores"},
        ))
        df = pl.DataFrame({"store_id": ["S1", "S2", "S99"]})
        context = {"allowed_stores": ["S1", "S2"]}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 1
        assert "unexpected" in issues[0].message.lower()

    def test_no_context_returns_empty(self):
        rule = UnexpectedEntity(ValidationRule(
            name="unexpected_entity",
            rule_type="unexpected_entity",
            parameters={"entity_column": "store_id"},
        ))
        df = pl.DataFrame({"store_id": ["S1"]})
        issues = rule.evaluate(df)
        assert len(issues) == 0


class TestValueRangeCheck:
    def test_pass_within_range(self):
        rule = ValueRangeCheck(ValidationRule(
            name="value_range_check",
            rule_type="value_range_check",
            parameters={"column": "sales", "min": 0, "max": 1000},
        ))
        df = pl.DataFrame({"sales": [100, 200, 300]})
        issues = rule.evaluate(df)
        assert len(issues) == 0

    def test_fail_below_min(self):
        rule = ValueRangeCheck(ValidationRule(
            name="value_range_check",
            rule_type="value_range_check",
            parameters={"column": "sales", "min": 0, "max": 1000},
        ))
        df = pl.DataFrame({"sales": [-10, 200, 300]})
        issues = rule.evaluate(df)
        assert len(issues) == 1
        assert "below minimum" in issues[0].message

    def test_fail_above_max(self):
        rule = ValueRangeCheck(ValidationRule(
            name="value_range_check",
            rule_type="value_range_check",
            parameters={"column": "sales", "min": 0, "max": 1000},
        ))
        df = pl.DataFrame({"sales": [100, 200, 1500]})
        issues = rule.evaluate(df)
        assert len(issues) == 1
        assert "above maximum" in issues[0].message

    def test_no_column_returns_empty(self):
        rule = ValueRangeCheck(ValidationRule(
            name="value_range_check",
            rule_type="value_range_check",
            parameters={"column": "nonexistent"},
        ))
        df = pl.DataFrame({"sales": [100]})
        issues = rule.evaluate(df)
        assert len(issues) == 0


class TestToleranceCheck:
    def test_pass_within_tolerance(self):
        rule = ToleranceCheck(ValidationRule(
            name="tolerance_check",
            rule_type="tolerance_check",
            parameters={"column": "sales", "tolerance": 0.05, "context_key": "expected"},
        ))
        df = pl.DataFrame({"sales": [100.0]})
        context = {"expected": {"sales": 102.0}}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 0

    def test_fail_outside_tolerance(self):
        rule = ToleranceCheck(ValidationRule(
            name="tolerance_check",
            rule_type="tolerance_check",
            parameters={"column": "sales", "tolerance": 0.01, "context_key": "expected"},
        ))
        df = pl.DataFrame({"sales": [100.0]})
        context = {"expected": {"sales": 200.0}}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 1
        assert "differs" in issues[0].message

    def test_no_expected_returns_empty(self):
        rule = ToleranceCheck(ValidationRule(
            name="tolerance_check",
            rule_type="tolerance_check",
            parameters={"column": "sales", "tolerance": 0.01, "context_key": "expected"},
        ))
        df = pl.DataFrame({"sales": [100.0]})
        issues = rule.evaluate(df, context={})
        assert len(issues) == 0


class TestDifferencePercentageCheck:
    def test_pass_within_threshold(self):
        rule = DifferencePercentageCheck(ValidationRule(
            name="difference_percentage_check",
            rule_type="difference_percentage_check",
            parameters={"column": "sales", "threshold": 0.10, "context_key": "expected"},
        ))
        df = pl.DataFrame({"sales": [100.0]})
        context = {"expected": {"sales": 105.0}}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 0

    def test_fail_outside_threshold(self):
        rule = DifferencePercentageCheck(ValidationRule(
            name="difference_percentage_check",
            rule_type="difference_percentage_check",
            parameters={"column": "sales", "threshold": 0.05, "context_key": "expected"},
        ))
        df = pl.DataFrame({"sales": [100.0]})
        context = {"expected": {"sales": 200.0}}
        issues = rule.evaluate(df, context=context)
        assert len(issues) == 1
        assert "differs" in issues[0].message

    def test_no_expected_returns_empty(self):
        rule = DifferencePercentageCheck(ValidationRule(
            name="difference_percentage_check",
            rule_type="difference_percentage_check",
            parameters={"column": "sales", "threshold": 0.05, "context_key": "expected"},
        ))
        df = pl.DataFrame({"sales": [100.0]})
        issues = rule.evaluate(df, context={})
        assert len(issues) == 0
