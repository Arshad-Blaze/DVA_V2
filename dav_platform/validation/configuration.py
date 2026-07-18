"""Validation Layer — Configuration Builder."""

from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import (
    ValidationConfig,
    ValidationRule,
    ValidationSeverity,
)


class ValidationConfigBuilder:
    """Builder for ValidationConfig objects."""

    def __init__(self):
        self._rules: List[ValidationRule] = []
        self._check_completeness = True
        self._check_consistency = True
        self._check_uniqueness = True
        self._check_nulls = True
        self._check_ranges = True
        self._max_null_percentage = 10.0
        self._required_columns: List[str] = []
        self._column_ranges: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, Any] = {}

    def add_rule(self, rule: ValidationRule) -> "ValidationConfigBuilder":
        self._rules.append(rule)
        return self

    def add_rules(self, rules: List[ValidationRule]) -> "ValidationConfigBuilder":
        self._rules.extend(rules)
        return self

    def check_completeness(self, enabled: bool = True) -> "ValidationConfigBuilder":
        self._check_completeness = enabled
        return self

    def check_consistency(self, enabled: bool = True) -> "ValidationConfigBuilder":
        self._check_consistency = enabled
        return self

    def check_uniqueness(self, enabled: bool = True) -> "ValidationConfigBuilder":
        self._check_uniqueness = enabled
        return self

    def check_nulls(self, enabled: bool = True) -> "ValidationConfigBuilder":
        self._check_nulls = enabled
        return self

    def check_ranges(self, enabled: bool = True) -> "ValidationConfigBuilder":
        self._check_ranges = enabled
        return self

    def max_null_percentage(self, pct: float) -> "ValidationConfigBuilder":
        self._max_null_percentage = pct
        return self

    def required_columns(self, cols: List[str]) -> "ValidationConfigBuilder":
        self._required_columns = cols
        return self

    def column_range(self, col: str, min_val: Any = None, max_val: Any = None) -> "ValidationConfigBuilder":
        self._column_ranges[col] = {}
        if min_val is not None:
            self._column_ranges[col]["min"] = min_val
        if max_val is not None:
            self._column_ranges[col]["max"] = max_val
        return self

    def metadata(self, key: str, value: Any) -> "ValidationConfigBuilder":
        self._metadata[key] = value
        return self

    def build(self) -> ValidationConfig:
        return ValidationConfig(
            rules=self._rules,
            check_completeness=self._check_completeness,
            check_consistency=self._check_consistency,
            check_uniqueness=self._check_uniqueness,
            check_nulls=self._check_nulls,
            check_ranges=self._check_ranges,
            max_null_percentage=self._max_null_percentage,
            required_columns=self._required_columns,
            column_ranges=self._column_ranges,
            metadata=self._metadata,
        )


def build_validation_config(
    rules: Optional[List[ValidationRule]] = None,
    required_columns: Optional[List[str]] = None,
    max_null_percentage: float = 10.0,
    **kwargs,
) -> ValidationConfig:
    """Convenience function to build a ValidationConfig."""
    builder = ValidationConfigBuilder()
    if rules:
        builder.add_rules(rules)
    if required_columns:
        builder.required_columns(required_columns)
    builder.max_null_percentage(max_null_percentage)
    return builder.build()
