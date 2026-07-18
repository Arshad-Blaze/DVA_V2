"""Validation Layer — Metadata Collector."""

from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import ValidationIssue


class MetadataCollector:
    """Collects and organizes validation metadata."""

    def __init__(self):
        self._data: Dict[str, Any] = {
            "rules_evaluated": [],
            "rules_passed": [],
            "rules_failed": [],
            "tolerances_used": [],
            "thresholds_applied": [],
            "warnings": [],
            "errors": [],
        }

    def record_rule_evaluated(self, rule_name: str):
        self._data["rules_evaluated"].append(rule_name)

    def record_rule_passed(self, rule_name: str):
        self._data["rules_passed"].append(rule_name)

    def record_rule_failed(self, rule_name: str, issues: List[ValidationIssue]):
        self._data["rules_failed"].append(rule_name)
        for issue in issues:
            entry = {"rule": rule_name, "message": issue.message, "severity": issue.severity.value}
            if issue.column:
                entry["column"] = issue.column
            if issue.severity.value in ("error", "critical"):
                self._data["errors"].append(entry)
            elif issue.severity.value == "warning":
                self._data["warnings"].append(entry)

    def record_tolerance(self, rule_name: str, tolerance: float):
        self._data["tolerances_used"].append({"rule": rule_name, "tolerance": tolerance})

    def record_threshold(self, rule_name: str, threshold: float):
        self._data["thresholds_applied"].append({"rule": rule_name, "threshold": threshold})

    def set_duration(self, seconds: float):
        self._data["execution_duration_seconds"] = seconds

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "rules_evaluated_count": len(self._data["rules_evaluated"]),
            "rules_passed_count": len(self._data["rules_passed"]),
            "rules_failed_count": len(self._data["rules_failed"]),
            "warning_count": len(self._data["warnings"]),
            "error_count": len(self._data["errors"]),
            "tolerances_used": self._data["tolerances_used"],
            "thresholds_applied": self._data["thresholds_applied"],
            "execution_duration_seconds": self._data.get("execution_duration_seconds", 0.0),
        }
