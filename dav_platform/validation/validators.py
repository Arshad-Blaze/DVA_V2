"""Validation Layer — Built-in Validators.

Each validator is a pluggable strategy registered in the RuleRegistry.
"""

from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import ValidationIssue, ValidationSeverity, ValidationRule
from dav_platform.validation.rules import BaseValidationRule, register_rule


@register_rule
class NullRequiredFields(BaseValidationRule):
    """Check that required columns have no nulls."""
    RULE_NAME = "null_required_fields"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        columns = self.parameters.get("columns", [])
        if not columns:
            columns = [c for c in df.columns if c in self.rule_def.columns]
        issues = []
        for col in columns:
            if col not in df.columns:
                issues.append(ValidationIssue(
                    rule=self.name, message=f"Column '{col}' not found in data",
                    severity=ValidationSeverity.ERROR, column=col,
                ))
                continue
            null_count = df[col].null_count()
            if null_count > 0:
                issues.append(ValidationIssue(
                    rule=self.name,
                    message=f"Column '{col}' has {null_count} null values",
                    severity=self.severity, row_count=null_count, column=col,
                ))
        return issues


@register_rule
class DuplicateDetection(BaseValidationRule):
    """Detect duplicate rows based on key columns."""
    RULE_NAME = "duplicate_detection"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        key_columns = self.parameters.get("columns", [])
        if not key_columns:
            key_columns = [c for c in df.columns if c in self.rule_def.columns]
        if not key_columns:
            return []
        existing = [c for c in key_columns if c in df.columns]
        if not existing:
            return []
        before = df.height
        deduped = df.unique(subset=existing)
        after = deduped.height
        dup_count = before - after
        if dup_count > 0:
            return [ValidationIssue(
                rule=self.name,
                message=f"Found {dup_count} duplicate rows on columns {existing}",
                severity=self.severity, row_count=dup_count,
            )]
        return []


@register_rule
class MissingEntity(BaseValidationRule):
    """Check for missing entities (stores, UPCs, etc.) against expected list."""
    RULE_NAME = "missing_entity"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        entity_column = self.parameters.get("entity_column", "")
        expected_key = self.parameters.get("context_key", "expected_entities")
        if not entity_column or entity_column not in df.columns:
            return []
        expected = (context or {}).get(expected_key, [])
        if not expected:
            return []
        actual = set(df[entity_column].unique().to_list())
        missing = set(expected) - actual
        if missing:
            return [ValidationIssue(
                rule=self.name,
                message=f"Missing {len(missing)} expected entities in '{entity_column}'",
                severity=self.severity, row_count=len(missing), column=entity_column,
            )]
        return []


@register_rule
class UnexpectedEntity(BaseValidationRule):
    """Check for unexpected entities not in expected list."""
    RULE_NAME = "unexpected_entity"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        entity_column = self.parameters.get("entity_column", "")
        expected_key = self.parameters.get("context_key", "allowed_entities")
        if not entity_column or entity_column not in df.columns:
            return []
        allowed = (context or {}).get(expected_key, [])
        if not allowed:
            return []
        actual = set(df[entity_column].unique().to_list())
        unexpected = actual - set(allowed)
        if unexpected:
            sample = list(unexpected)[:5]
            return [ValidationIssue(
                rule=self.name,
                message=f"Found {len(unexpected)} unexpected entities in '{entity_column}': {sample}",
                severity=self.severity, row_count=len(unexpected), column=entity_column,
            )]
        return []


@register_rule
class ValueRangeCheck(BaseValidationRule):
    """Check that numeric values fall within expected ranges."""
    RULE_NAME = "value_range_check"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        column = self.parameters.get("column", "")
        if not column or column not in df.columns:
            return []
        min_val = self.parameters.get("min")
        max_val = self.parameters.get("max")
        issues = []
        if min_val is not None:
            below = df.filter(pl.col(column) < min_val).height
            if below > 0:
                issues.append(ValidationIssue(
                    rule=self.name,
                    message=f"{below} rows in '{column}' below minimum {min_val}",
                    severity=self.severity, row_count=below, column=column,
                ))
        if max_val is not None:
            above = df.filter(pl.col(column) > max_val).height
            if above > 0:
                issues.append(ValidationIssue(
                    rule=self.name,
                    message=f"{above} rows in '{column}' above maximum {max_val}",
                    severity=self.severity, row_count=above, column=column,
                ))
        return issues


@register_rule
class ToleranceCheck(BaseValidationRule):
    """Check that differences between expected and actual are within tolerance."""
    RULE_NAME = "tolerance_check"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        expected_key = self.parameters.get("context_key", "expected_totals")
        tolerance = self.parameters.get("tolerance", 0.01)
        column = self.parameters.get("column", "")
        total_column = self.parameters.get("total_column", column)

        expected_totals = (context or {}).get(expected_key, {})
        if not expected_totals or not total_column or total_column not in df.columns:
            return []

        issues = []
        total = df[total_column].sum()
        expected_val = expected_totals.get(total_column)
        if expected_val is not None and expected_val != 0:
            diff_pct = abs(total - expected_val) / abs(expected_val)
            if diff_pct > tolerance:
                issues.append(ValidationIssue(
                    rule=self.name,
                    message=f"'{total_column}' differs by {diff_pct:.2%} from expected {expected_val}",
                    severity=self.severity, column=total_column,
                ))
        return issues


@register_rule
class DifferencePercentageCheck(BaseValidationRule):
    """Check that difference percentage is within threshold."""
    RULE_NAME = "difference_percentage_check"

    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        if df.height == 0:
            return []
        threshold = self.parameters.get("threshold", 0.05)
        column = self.parameters.get("column", "")
        expected_key = self.parameters.get("context_key", "expected_totals")

        if not column or column not in df.columns:
            return []

        expected_totals = (context or {}).get(expected_key, {})
        expected_val = expected_totals.get(column)
        if expected_val is None:
            return []

        actual_val = df[column].sum()
        if expected_val == 0:
            return []
        diff_pct = abs(actual_val - expected_val) / abs(expected_val)
        if diff_pct > threshold:
            return [ValidationIssue(
                rule=self.name,
                message=f"'{column}' differs by {diff_pct:.2%} (threshold: {threshold:.2%})",
                severity=self.severity, column=column,
            )]
        return []
