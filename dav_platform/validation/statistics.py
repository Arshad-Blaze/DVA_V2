"""Validation Layer — Validation Statistics."""

from dav_platform.core.contracts import (
    ValidationResult,
    ValidationSeverity,
    ValidationStatistics,
)


class ValidationStatisticsEngine:
    """Computes aggregate statistics from validation results."""

    def compute(
        self,
        result: ValidationResult,
        rules_evaluated: int,
        execution_time: float,
    ) -> ValidationStatistics:
        warning_count = sum(
            1 for i in result.issues if i.severity == ValidationSeverity.WARNING
        )
        error_count = sum(
            1 for i in result.issues if i.severity == ValidationSeverity.ERROR
        )
        critical_count = sum(
            1 for i in result.issues if i.severity == ValidationSeverity.CRITICAL
        )
        rules_passed = rules_evaluated - result.error_count - warning_count - critical_count
        if rules_evaluated > 0:
            coverage = (result.total_rows_checked / max(result.total_rows_checked, 1)) * 100
        else:
            coverage = 0.0

        return ValidationStatistics(
            total_rules_evaluated=rules_evaluated,
            rules_passed=max(0, rules_passed),
            rules_failed=result.error_count + critical_count,
            warning_count=warning_count,
            error_count=error_count,
            critical_count=critical_count,
            validation_coverage=coverage,
            execution_time_seconds=execution_time,
            total_entities_checked=result.total_rows_checked,
        )
