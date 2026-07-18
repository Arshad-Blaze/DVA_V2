"""Validation Layer — Report Builder."""

from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import (
    ValidationIssue,
    ValidationResult,
    ValidationReportData,
    ValidationStatistics,
    ValidationSummary,
)


class ValidationReportBuilder:
    """Builds structured ValidationReportData from validation results."""

    def __init__(self):
        self._summaries: List[ValidationSummary] = []
        self._statistics: Optional[ValidationStatistics] = None
        self._metadata: Dict[str, Any] = {}

    def add_summary(self, summary: ValidationSummary) -> "ValidationReportBuilder":
        self._summaries.append(summary)
        return self

    def add_summaries(self, summaries: List[ValidationSummary]) -> "ValidationReportBuilder":
        self._summaries.extend(summaries)
        return self

    def statistics(self, stats: ValidationStatistics) -> "ValidationReportBuilder":
        self._statistics = stats
        return self

    def metadata(self, key: str, value: Any) -> "ValidationReportBuilder":
        self._metadata[key] = value
        return self

    def build(
        self,
        result: ValidationResult,
        summaries: Optional[List[ValidationSummary]] = None,
    ) -> ValidationReportData:
        all_summaries = list(self._summaries)
        if summaries:
            all_summaries.extend(summaries)

        total_checks = self._statistics.total_rules_evaluated if self._statistics else 0
        failed_checks = self._statistics.rules_failed if self._statistics else 0
        passed_checks = total_checks - failed_checks

        return ValidationReportData(
            passed=result.passed,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            summaries=all_summaries,
            issues=result.issues,
            statistics=self._statistics,
            metadata=self._metadata,
        )
